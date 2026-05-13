import secrets
import string


def generate_password(length: int = 12, use_digits: bool = True,
                      use_punctuation: bool = True) -> str:
    """
    Генерация криптографически стойкого пароля.

    Аргументы:
        length (int): Длина пароля (по умолчанию 12)
        use_digits (bool): Включать ли цифры (по умолчанию True)
        use_punctuation (bool): Включать ли спецсимволы (по умолчанию True)

    Возвращает:
        str: Сгенерированный пароль
    """
    if length < 4:
        raise ValueError("Длина пароля должна быть не менее 4 символов")


    chars = string.ascii_letters


    if use_digits:
        chars += string.digits


    if use_punctuation:
        chars += string.punctuation


    password = ''.join(secrets.choice(chars) for _ in range(length))
    return password