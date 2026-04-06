"""Test filtering through web interface"""

import sys
sys.path.insert(0, '/home/sel-jari/Desktop/IA-Responsable')

from app import create_app, db
from app.models import User, Request, AuditLog
from datetime import datetime

app = create_app()

# Create test context
with app.app_context():
    # Check if test user exists
    test_user = User.query.filter_by(username='testuser').first()
    if not test_user:
        test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash='hashed_test_password',
            role='user'
        )
        db.session.add(test_user)
        db.session.commit()
        print("✓ Test user created")
    else:
        print("✓ Test user exists")
    
    # Simulate a filtered request attempt
    print("\nSimulating filtered request with email...")
    
    from app.utils.security import filter_user_input
    
    test_content = "My email is john@example.com, can you help?"
    is_safe, error_msg, details = filter_user_input(test_content)
    
    print(f"Content: {test_content}")
    print(f"Safe: {is_safe}")
    print(f"Error: {error_msg}")
    
    # Log the attempt
    audit_log = AuditLog(
        user_id=test_user.id,
        action='DEMANDE_FILTREE',
        details=f"Contenu rejeté : {', '.join(details)}",
        severity='warning'
    )
    db.session.add(audit_log)
    db.session.commit()
    
    print("\n✓ Audit log created for filtered request")
    
    # Check audit logs
    logs = AuditLog.query.filter_by(user_id=test_user.id, action='DEMANDE_FILTREE').all()
    print(f"✓ Found {len(logs)} filtered request log(s)")
    
    if logs:
        latest = logs[-1]
        print(f"  - Time: {latest.created_at}")
        print(f"  - Details: {latest.details}")

