"""
Gerenciador de política criptográfica adaptativa.

Responsável por:
1. Receber o nível de segurança requerido pelo sistema fuzzy.
2. Selecionar a política criptográfica correspondente.
3. Realizar criptografia e descriptografia utilizando AES-GCM.

A decisão sobre o nível de segurança NÃO é realizada neste módulo.
Ela é definida pelo fuzzy_security.py.
"""

import os

from Crypto.Cipher import AES


class CryptoManager:
    """
    Gerencia a política criptográfica adaptativa do dispositivo.

    A política é definida a partir do nível de segurança requerido
    produzido pelo sistema fuzzy.
    """

    POLICIES = {
        "BAIXO": {
            "algorithm": "AES-128",
            "key_size": 16,
            "security_level": 1,
        },
        "MODERADO": {
            "algorithm": "AES-128",
            "key_size": 16,
            "security_level": 2,
        },
        "ALTO": {
            "algorithm": "AES-192",
            "key_size": 24,
            "security_level": 3,
        },
        "MUITO ALTO": {
            "algorithm": "AES-256",
            "key_size": 32,
            "security_level": 4,
        },
    }

    def __init__(self):
        """Inicializa o gerenciador."""
        self.current_policy = None
        self.current_key = None

    def select_policy(self, security_level):
        """
        Seleciona a política criptográfica com base no nível
        de segurança requerido pelo sistema fuzzy.

        Parâmetros
        ----------
        security_level : str
            Nível retornado pelo fuzzy_security.py.

        Retorno
        -------
        dict
            Política criptográfica selecionada.
        """

        security_level = security_level.upper().strip()

        if security_level not in self.POLICIES:
            raise ValueError(
                f"Nível de segurança inválido: {security_level}"
            )

        policy = self.POLICIES[security_level]

        # Gera uma nova chave caso a política tenha mudado
        if (
            self.current_policy is None
            or self.current_policy["algorithm"] != policy["algorithm"]
        ):
            self.current_key = os.urandom(policy["key_size"])

        self.current_policy = policy

        return policy.copy()

    def get_current_policy(self):
        """
        Retorna a política criptográfica atualmente utilizada.
        """

        if self.current_policy is None:
            return None

        return self.current_policy.copy()

    def encrypt(self, data):
        """
        Criptografa dados utilizando a política atualmente selecionada.

        O algoritmo utilizado é AES-GCM.

        Parâmetros
        ----------
        data : bytes
            Dados a serem criptografados.

        Retorno
        -------
        dict
            Contém nonce, ciphertext e tag.
        """

        if self.current_policy is None:
            raise RuntimeError(
                "Nenhuma política criptográfica foi selecionada."
            )

        if not isinstance(data, bytes):
            raise TypeError("Os dados devem estar em formato bytes.")

        cipher = AES.new(
            self.current_key,
            AES.MODE_GCM
        )

        ciphertext, tag = cipher.encrypt_and_digest(data)

        return {
            "algorithm": self.current_policy["algorithm"],
            "nonce": cipher.nonce,
            "ciphertext": ciphertext,
            "tag": tag,
        }

    def decrypt(self, encrypted_data):
        """
        Descriptografa dados utilizando a chave atual.

        Parâmetros
        ----------
        encrypted_data : dict
            Estrutura retornada pelo método encrypt().

        Retorno
        -------
        bytes
            Dados originais descriptografados.
        """

        if self.current_policy is None:
            raise RuntimeError(
                "Nenhuma política criptográfica foi selecionada."
            )

        cipher = AES.new(
            self.current_key,
            AES.MODE_GCM,
            nonce=encrypted_data["nonce"]
        )

        data = cipher.decrypt_and_verify(
            encrypted_data["ciphertext"],
            encrypted_data["tag"]
        )

        return data


if __name__ == "__main__":

    print("=" * 60)
    print("TESTE DO GERENCIADOR CRIPTOGRÁFICO ADAPTATIVO")
    print("=" * 60)

    crypto = CryptoManager()

    casos = [
        ("BAIXO", "AES-128"),
        ("MODERADO", "AES-128"),
        ("ALTO", "AES-192"),
        ("MUITO ALTO", "AES-256"),
    ]

    for nivel, algoritmo_esperado in casos:

        policy = crypto.select_policy(nivel)

        print(f"\nNível de segurança: {nivel}")
        print(f"Algoritmo selecionado: {policy['algorithm']}")
        print(f"Tamanho da chave: {policy['key_size'] * 8} bits")

        assert policy["algorithm"] == algoritmo_esperado

    print("\n" + "-" * 60)
    print("TESTE DE CRIPTOGRAFIA")
    print("-" * 60)

    crypto.select_policy("MUITO ALTO")

    mensagem = b"Dados de telemetria do dispositivo IoT"

    encrypted = crypto.encrypt(mensagem)
    decrypted = crypto.decrypt(encrypted)

    print(f"Algoritmo utilizado: {encrypted['algorithm']}")
    print(f"Mensagem original: {mensagem.decode()}")
    print(f"Mensagem descriptografada: {decrypted.decode()}")

    assert decrypted == mensagem

    print("\nCriptografia e descriptografia realizadas com sucesso.")

    print("\n" + "=" * 60)
    print("TESTE CONCLUÍDO")
    print("=" * 60)