from dataclasses import dataclass
import uuid

def _salt(n: int = 6) -> str:
    return uuid.uuid4().hex[:n]

@dataclass(frozen=True, slots=True)
class FakeUser:
    username: str
    email: str
    senha: str
    nome: str
    matricula: str

    @staticmethod
    def new(prefix: str = "user", domain: str = "teste.com", salt_len: int = 6) -> "FakeUser":
        s = _salt(salt_len)
        return FakeUser(
            username=f"{prefix}_{s}",
            email=f"{prefix}_{s}@{domain}",
            senha=f"Senha@{s}",
            nome="Usuário de Teste",
            matricula=f"C{s.upper()}",
        )

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "email": self.email,
            "senha": self.senha,
            "nome": self.nome,
            "matricula": self.matricula,
        }
