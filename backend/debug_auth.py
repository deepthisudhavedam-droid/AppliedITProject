import uuid
from database.connection import SessionLocal
from services.auth_service import register_user, authenticate_user, create_access_token_for_user
from models.auth_schemas import UserResponse, TokenResponse


def run_test():
    db = SessionLocal()
    try:
        email = 'debug_test@example.com'
        password = 'Debug1234'
        username = 'debug_test'

        print('Creating user', email)
        user = register_user(db, username, email, password)
        print('Created user:', user.id, user.email, user.username, getattr(user, 'created_at', None))

        print('Authenticating user...')
        auth_user = authenticate_user(db, email, password)
        print('authenticate_user returned:', auth_user)

        if auth_user is None:
            print('AUTH FAILED')
            return

        try:
            token = create_access_token_for_user(auth_user)
            print('Token created:', token[:30], '...')
        except Exception as e:
            print('Token creation failed:', type(e).__name__, e)
            raise

        try:
            user_resp = UserResponse.from_orm(auth_user)
            print('UserResponse from orm OK:', user_resp)
        except Exception as e:
            print('UserResponse.from_orm failed:', type(e).__name__, e)
            raise

        try:
            token_resp = TokenResponse(access_token=token, token_type='bearer', user=user_resp)
            print('TokenResponse created:', token_resp)
        except Exception as e:
            print('TokenResponse creation failed:', type(e).__name__, e)
            raise

    finally:
        db.close()


if __name__ == '__main__':
    run_test()
