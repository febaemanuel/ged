# GED System - Codebase Structure & Security Analysis

## Executive Summary
This is a **Flask-based Document Management System (GED)** implementing a UGQ workflow for EBSERH healthcare institution. The system manages document lifecycle from creation through approval to publication.

---

## 1. Framework & Architecture

### Framework
- **Web Framework**: Flask 3.0.0
- **ORM**: Flask-SQLAlchemy 3.1.1 with SQLAlchemy 2.0.23
- **Database**: PostgreSQL (psycopg2)
- **Authentication**: Flask-Login 0.6.3
- **Email**: Flask-Mail 0.10.0

### Architecture Pattern
- **MVC Pattern**: Models, Routes (Controllers), Services
- **Blueprint-based modular routing**
- **Service layer for business logic** (workflow, email, AI integration)
- **Factory pattern** for app initialization

### Key Directory Structure
```
/home/user/ged/
├── app/
│   ├── models/
│   │   └── models.py (553 lines) - All database models
│   ├── routes/ (4,271 lines total)
│   │   ├── routes_view.py (1,301 lines) - HTML template routes
│   │   ├── routes_documento.py (921 lines) - Document API endpoints
│   │   ├── routes_dashboard.py (613 lines) - Dashboard & reports
│   │   ├── routes_ia.py (477 lines) - AI integration endpoints
│   │   ├── routes_tarefa.py (465 lines) - Task management
│   │   └── routes_busca.py (212 lines) - Search functionality
│   └── services/ (3,310 lines total)
│       ├── workflow.py (1,310 lines) - UGQ workflow automation
│       ├── ai_client.py (654 lines) - DeepSeek AI integration
│       ├── email_service.py (352 lines) - Email notifications
│       └── report_generator.py (395 lines) - PDF reports
├── app.py (139 lines) - Entry point
└── config.py (196 lines) - Configuration
```

---

## 2. Database Models

### Core Models
1. **Usuario** - User accounts with roles (admin, gerente, comum, triador_ugq, validador_ugq)
2. **Documento** - Document records with lifecycle states
3. **Tarefa** - Tasks/assignments in the workflow
4. **LogAI** - Audit logs for AI API calls
5. **BlocoAssinatura** - Signature blocks for multi-person approval
6. **ItemBlocoAssinatura** - Individual signature items
7. **ListaMestra** - Master list for published documents (UGQ)
8. **ValidacaoUGQ** - UGQ validation records
9. **Notificacao** - User notifications

### Key Fields
- `codigo_unico`: Permanent document identifier (DOC-YYYYMMDD-HHMMSS-XXX)
- `codigo_provisorio`: Temporary code during workflow
- `codigo_definitivo`: Final code assigned by UGQ (TIPO.SETOR-NNN)
- `arquivo_original`, `arquivo_publicado_pdf`, `arquivo_final`: File references
- `status`: Document lifecycle state

---

## 3. Security Vulnerabilities Identified

### CRITICAL ISSUES

#### 1. Path Traversal Vulnerability (HIGH SEVERITY)
**Location**: `/home/user/ged/app/routes/routes_view.py` lines 447-469
```python
# VULNERABLE CODE
caminho_pdf = os.path.join(Config.ASSINATURAS_FOLDER, documento.arquivo_final)
return send_file(caminho_pdf, as_attachment=True, ...)
```

**Issue**: `documento.arquivo_final` is directly concatenated without path validation
**Attack Vector**: If `arquivo_final` contains `../`, arbitrary files could be accessed
**Risk**: Medium (mitigated by database-only updates, but still present)
**Recommendation**: 
- Use `os.path.normpath()` and validate resulting path is within base directory
- Implement whitelist validation on arquivo_final values

#### 2. Missing Path Normalization in File Downloads
**Location**: `/home/user/ged/app/routes/routes_documento.py` lines 330-357
```python
# POTENTIALLY VULNERABLE
caminho = os.path.join(current_app.config['UPLOAD_FOLDER'], documento.arquivo_original)
return send_file(caminho, as_attachment=True, ...)
```

**Issue**: While `secure_filename()` is used during upload, downloaded paths lack normalization
**Recommendation**: Add validation before send_file():
```python
real_path = os.path.normpath(caminho)
base_dir = os.path.normpath(current_app.config['UPLOAD_FOLDER'])
if not real_path.startswith(base_dir):
    abort(403)
```

#### 3. Missing CSRF Protection
**Finding**: No Flask-WTF or CSRF tokens found
**Affected**: All POST/PUT/DELETE endpoints
**Files**: All routes accept state-changing requests without CSRF validation
**Recommendation**: 
- Install: `pip install Flask-WTF`
- Add CSRF middleware and tokens to all forms

#### 4. Weak Password Validation
**Location**: `/home/user/ged/app/routes/routes_auth.py` line 175
```python
if len(senha_nova) < 6:  # Only 6 characters minimum!
    return jsonify({'erro': 'Nova senha deve ter no mínimo 6 caracteres'}), 400
```
**Issue**: Minimum 6 character password is insufficient
**Recommendation**: Increase to 12+ characters, enforce complexity (uppercase, numbers, special chars)

#### 5. Hardcoded Credentials in Development Config
**Location**: `/home/user/ged/config.py` line 26
```python
_db_uri = os.environ.get('DATABASE_URL') or \
    'postgresql://ged_user:ged_password@localhost:5432/ged_db'
```
**Issue**: Credentials hardcoded as fallback
**Recommendation**: Remove fallback, require environment variable in all environments

#### 6. Admin Default Credentials
**Location**: `/home/user/ged/app.py` lines 62-71
```python
admin = Usuario.query.filter_by(email='admin@example.com').first()
if not admin:
    admin = Usuario(...)
    admin.set_password('admin123')  # WEAK DEFAULT!
```
**Issue**: Well-known default credentials
**Recommendation**: Force password change on first login or remove seeding from code

---

### HIGH SEVERITY ISSUES

#### 7. Insufficient Access Control on File Downloads
**Location**: `/home/user/ged/app/routes/routes_view.py` lines 416-444
```python
@view_bp.route('/documento/<int:id>/download')
def documento_download(id):
    documento = Documento.query.get_or_404(id)
    
    if documento.status != 'Publicado':
        if not current_user.is_authenticated:
            flash('Este documento requer autenticação', 'warning')
            return redirect(url_for('view.login'))
        # Verifies permission but allows admin to download ANY document
```

**Issue**: Admins can download any document regardless of workflow status or sensitivity
**Recommendation**: Implement fine-grained access control based on document status and user role

#### 8. Information Disclosure in Error Messages
**Location**: Multiple routes (dashboard, documento, etc.)
```python
caminho_pdf = os.path.join(Config.ASSINATURAS_FOLDER, documento.arquivo_final)
if not os.path.exists(caminho_pdf):
    flash(f'Arquivo PDF de assinaturas não encontrado no caminho: {caminho_pdf}', 'danger')
```
**Issue**: Full file paths exposed in user-facing error messages
**Recommendation**: Return generic error messages, log full paths server-side only

#### 9. Weak Random Number Generation for Document Codes
**Location**: `/home/user/ged/app/models/models.py` lines 149-152
```python
import random
random_suffix = f"{random.randint(0, 999):03d}"
self.codigo_unico = f"DOC-{timestamp}-{random_suffix}"
```
**Issue**: Uses `random` not `secrets` - predictable and not cryptographically secure
**Recommendation**: Use `secrets.randbelow(1000)` or `uuid4()`

#### 10. SQL Injection via Unvalidated Filters
**Location**: Multiple routes
```python
# In routes_documento.py
if busca:
    query = query.filter(
        Documento.titulo.ilike(f'%{busca}%')  # ilike is parameterized, safe
    )
```
**Assessment**: Safe due to SQLAlchemy ORM parameterization, but worth noting

#### 11. Unvalidated JSONJSON Deserialization
**Location**: `/home/user/ged/app/models/models.py` lines 206-213
```python
def get_metadados(self):
    if self.metadados_json:
        try:
            return json.loads(self.metadados_json)
        except:
            return {}
```
**Issue**: Bare except clause hides errors; no validation of JSON structure
**Recommendation**: 
```python
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON in metadados: {e}")
    return {}
```

---

### MEDIUM SEVERITY ISSUES

#### 12. Session Cookie Security Issues
**Location**: `/home/user/ged/config.py` lines 57-59
```python
SESSION_COOKIE_HTTPONLY = True  # Good
SESSION_COOKIE_SAMESITE = 'Lax'  # Should be 'Strict'
# Missing: SESSION_COOKIE_SECURE = True (only in Production)
```
**Recommendation**: Set `SESSION_COOKIE_SECURE = True` in production config

#### 13. Audit Logging Gaps
**Finding**: No comprehensive audit trail for:
- Who modified documents
- When status changed
- Workflow transitions beyond task completion

**Recommendation**: Add audit_log table and middleware to track all state changes

#### 14. Email Configuration Not Validated
**Location**: `/home/user/ged/config.py` lines 68-76
```python
MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'  # Fallback
MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or ''  # Empty fallback!
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''  # Empty fallback!
```
**Issue**: Missing environment variables fail silently, email may not work
**Recommendation**: Validate required config on startup

#### 15. File Upload Restrictions Insufficient
**Location**: `/home/user/ged/config.py` line 53
```python
ALLOWED_EXTENSIONS = {'doc', 'docx', 'odt', 'pdf'}
```
**Issue**: Only checks extension, not MIME type. Could accept disguised executables.
**Recommendation**: Validate MIME type, scan with antivirus (e.g., yara)

#### 16. Debug Mode Exposed in Entry Point
**Location**: `/home/user/ged/app.py` line 138
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # debug=True!
```
**Issue**: Debug mode enabled, listening on 0.0.0.0 (all interfaces)
**Recommendation**: Use gunicorn/uWSGI, never set debug=True in production

---

### LOW SEVERITY ISSUES

#### 17. Bare Exception Handlers
**Locations**: Multiple files
```python
try:
    # code
except:  # Catches all exceptions including KeyboardInterrupt!
    return {}
```
**Recommendation**: Catch specific exceptions only

#### 18. Insufficient Input Validation for Dates
**Location**: `/home/user/ged/app/routes/routes_view.py` line 652
```python
prazo_dt = datetime.strptime(prazo, '%Y-%m-%d')  # No format validation error handling
```
**Recommendation**: Wrap in try-except, return validation error

#### 19. Timing Attack Vulnerability in Password Check
**Location**: Uses werkzeug's `check_password_hash()` which is constant-time, so this is SAFE

#### 20. No Rate Limiting
**Finding**: No rate limiting on login attempts or API endpoints
**Recommendation**: Implement Flask-Limiter to prevent brute force attacks

---

## 4. Current Security Implementations (Positive)

✓ **Password Hashing**: Using werkzeug's `generate_password_hash()` (PBKDF2)
✓ **ORM Protection**: SQLAlchemy prevents SQL injection
✓ **Login Authentication**: Flask-Login with session management  
✓ **HTTPOnly Cookies**: Prevents XSS credential theft
✓ **Secure Filename**: Using `secure_filename()` for uploads
✓ **User Roles**: Implemented role-based access control
✓ **File Path Validation**: Database ID lookups prevent direct path access (mostly)
✓ **Email Verification**: User accounts use email field uniqueness
✓ **Logging**: RotatingFileHandler for audit logs

---

## 5. Route Files Summary

| File | Lines | Purpose | Security Issues |
|------|-------|---------|-----------------|
| **routes_view.py** | 1,301 | HTML template rendering, document CRUD | Path traversal, info disclosure, missing CSRF |
| **routes_documento.py** | 921 | REST API for documents | Path traversal in downloads |
| **routes_dashboard.py** | 613 | Dashboard, statistics, PDF reports | Sensitive data in error messages |
| **routes_ia.py** | 477 | DeepSeek AI integration | API key exposure risk |
| **routes_tarefa.py** | 465 | Task workflow management | Access control gaps |
| **routes_busca.py** | 212 | Document search | Safe (parameterized queries) |

---

## 6. Files Requiring Immediate Attention

### Priority 1 (CRITICAL)
1. `/home/user/ged/app/routes/routes_view.py` - Line 458 (path traversal)
2. `/home/user/ged/app/routes/routes_documento.py` - Lines 344-357 (file download security)
3. `/home/user/ged/config.py` - Lines 21, 26 (credentials, secret key)

### Priority 2 (HIGH)
4. `/home/user/ged/app.py` - Line 138 (debug mode)
5. `/home/user/ged/app/routes/routes_auth.py` - Line 175 (password policy)
6. All routes - Add CSRF protection (Flask-WTF)

### Priority 3 (MEDIUM)
7. `/home/user/ged/app/models/models.py` - Lines 149-152 (weak RNG)
8. `/home/user/ged/app/services/workflow.py` - Line 1101 (filename generation)
9. All error handlers - Remove file paths from error messages

---

## 7. Architecture Assessment

### Strengths
- Clear separation of concerns (models, routes, services)
- Modular blueprint-based routing
- Comprehensive workflow service layer
- Database relationships properly defined

### Weaknesses
- No middleware for security headers
- Missing API request validation/schema enforcement
- No data encryption for sensitive fields (passwords are hashed, but other sensitive data like IP addresses stored in plaintext)
- Limited audit trail capabilities
- No rate limiting or DDoS protection

---

## 8. Recommendations (Prioritized)

### Immediate Actions (Week 1)
1. Add CSRF protection via Flask-WTF
2. Fix path traversal in arquivo_final handling
3. Remove hardcoded credentials
4. Disable debug mode
5. Add path normalization to all file downloads

### Short Term (Week 2-3)
1. Implement input validation framework
2. Add comprehensive audit logging
3. Implement rate limiting on authentication endpoints
4. Enhance error handling (no path disclosure)
5. Use `secrets` module for token generation

### Medium Term (Month 1)
1. Add integration tests for security controls
2. Implement API schema validation (marshmallow/pydantic)
3. Add security headers middleware (CSP, X-Frame-Options, etc.)
4. Set up automated security scanning (SAST)
5. Implement file MIME type validation

### Long Term (Quarter 1)
1. Security audit by external firm
2. Implement encryption for sensitive data fields
3. Add comprehensive logging/monitoring
4. Conduct penetration testing
5. Implement security incident response plan

