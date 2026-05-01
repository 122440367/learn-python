import bcrypt
from sqlmodel import Session, select

from app.models.tb_user import User
from app.models.schemas import UserPublic


def _to_public(user: User | None) -> UserPublic | None:
    if user is None:
        return None
    return UserPublic(id=user.id, name=user.name, email=user.email)


# ── 密码工具（私有） ──────────────────────────────────────────


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


# ── 查询方法：返回 UserPublic（不含密码） ──────────────────────


def get_by_id(session: Session, user_id: int) -> UserPublic | None:
    return _to_public(session.get(User, user_id))


def get_by_email(session: Session, email: str) -> UserPublic | None:
    statement = select(User).where(User.email == email)
    return _to_public(session.exec(statement).first())


def get_by_name(session: Session, name: str) -> UserPublic | None:
    statement = select(User).where(User.name == name)
    return _to_public(session.exec(statement).first())


# ── 认证方法：封装密码验证，service 层无需接触哈希 ─────────────


def authenticate(session: Session, email: str, plain_password: str) -> tuple[UserPublic | None, str | None]:
    """
    验证用户登录凭据。
    Returns:
        (UserPublic, None)         — 认证成功
        (None, "not_found")        — 用户不存在
        (None, "wrong_password")   — 密码错误
    """
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    if user is None:
        return None, "not_found"
    if not verify_password(plain_password, user.password):
        return None, "wrong_password"
    return _to_public(user), None


def change_password(session: Session, user_id: int, old_plain: str, new_plain: str) -> str | None:
    """
    验证旧密码并更新为新密码。
    Returns:
        None              — 成功
        "not_found"       — 用户不存在
        "wrong_password"  — 旧密码错误
    """
    user = session.get(User, user_id)
    if user is None:
        return "not_found"
    if not verify_password(old_plain, user.password):
        return "wrong_password"
    user.password = hash_password(new_plain)
    session.add(user)
    session.commit()
    return None


# ── 写入方法 ─────────────────────────────────────────────────


def create(session: Session, name: str, email: str, plain_password: str) -> UserPublic:
    """创建用户，内部处理密码哈希。"""
    user = User(
        name=name,
        password=hash_password(plain_password),
        email=email,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return _to_public(user)


def set_name(session: Session, user_id: int, new_name: str) -> UserPublic | None:
    """更新用户名，返回更新后的 UserPublic 或 None（用户不存在）。"""
    user = session.get(User, user_id)
    if user is None:
        return None
    user.name = new_name
    session.add(user)
    session.commit()
    session.refresh(user)
    return _to_public(user)


def remove(session: Session, user_id: int) -> bool:
    """删除用户，返回是否成功。"""
    user = session.get(User, user_id)
    if user is None:
        return False
    session.delete(user)
    session.commit()
    return True
