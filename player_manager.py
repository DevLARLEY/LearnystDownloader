import base64
import hashlib
import re

import requests

from util import handle


class PlayerManager:
    UNMODIFIED_PLAYER_NAME = "original_player.js"

    def __init__(
            self,
            token: str,
            version: int,
            lc: int,
            player_file: str
    ):
        self.token = token
        self.version = version
        self.lc = lc
        self.player_file = player_file

    def get_player(self) -> bool:
        b64_token = base64.b64encode(self.token.encode())

        sha256 = hashlib.new('sha256')
        sha256.update(b64_token)
        hashed = sha256.hexdigest()

        response = requests.get(
            url=f'https://player.learnyst.com/{hashed[:32]}/{hashed[32:]}/index.js',
            params={
                "tk": b64_token.decode(),
                "version": self.version,
                "lc": self.lc
            }
        )
        if response.status_code != 200:
            return False

        open(self.UNMODIFIED_PLAYER_NAME, "w", encoding="utf-8").write(response.text)
        return True

    @staticmethod
    def _find_and_insert(
            index_js: str,
            insert_index: int,
            rexp: str,
            name: str
    ) -> str:
        results = re.findall(rexp, index_js)

        handle(results, f"RegEx can't locate function: {rexp}")
        handle(len(results) == 1, f"RegEx found too many ({len(results)}) function results")

        return index_js[:insert_index] + f'exports.{name}={results[0]};' + index_js[insert_index:]

    @staticmethod
    def _find_insert_index(
            index_js: str,
            rexp: str
    ) -> int:
        found = re.findall(rexp, index_js)
        handle(found, f"regex can't locate function: {rexp}")
        handle(len(found) == 1, f"regex found too many ({len(found)}) function results")
        return index_js.index(found[0])

    @staticmethod
    def _find_and_insert_function(
            index_js: str,
            insert_index: int,
            rexp: str,
            name: str,
            function: str
    ) -> str:
        results = re.findall(rexp, index_js)

        handle(results, f"RegEx can't locate function: {rexp}")
        handle(len(results) == 1, f"RegEx found too many ({len(results)}) function results")

        return index_js[:insert_index] + f'exports.{name}={function % results[0]};' + index_js[insert_index:]

    def inject_exports(self):
        index_js = open(self.UNMODIFIED_PLAYER_NAME, "r", encoding="utf-8").read()

        SET_DRM_DATA_RE = r"let (_0x\w{3,6})={},_0x\w{3,6}=0,_0x\w{3,6}=0"
        SET_DRM_DATA_FUNCTION = r"function(value,key){%s[key]=value;}"

        # ENCRYPT_WITH_MD5_RE = r"function (_0x\w{3,6})\(_0x\w{3,6}\){var _0x\w{3,6}=_0x\w{3,6},_0x\w{3,6}=100,_0x\w{3,6}=_0x\w{3,6}"
        SET_CURRENT_LICENSE_RE = r"function (_0x\w{3,6})\(_0x\w{3,6},_0x\w{3,6},_0x\w{3,6},_0x\w{3,6},_0x\w{3,6}\){var _0x\w{3,6}=_0x\w{3,6};const _0x\w{3,6}=_0x\w{3,6}\(_0x\w{3,6},_0x\w{3,6},_0x\w{3,6},_0x\w{3,6},_0x\w{3,6}\);var _0x\w{3,6}={};return"
        ECRYPT_DECRYPT_BYTES_RE = r"(window\[_0x\w{3,6}\(\w+\)\])=function\(_0x\w{3,6},_0x\w{3,6},_0x\w{3,6}\)"
        ECRYPT_DECRYPTK_RE = r"function (_0x\w{3,6})\(_0x\w{3,6}\){var _0x\w{3,6}=_0x\w{3,6},_0x\w{3,6}=_0x\w{3,6}\[_0x\w{3,6}\(\w*\)\]\(_0x\w{3,6},_0x\w{3,6}\(\w*\)\)"

        INSERT_RE = r"exports\.getLicenseRequest=_0x\w{3,6};"
        index = self._find_insert_index(index_js, INSERT_RE)

        index_js = self._find_and_insert_function(index_js, index, SET_DRM_DATA_RE, "setDrmData", SET_DRM_DATA_FUNCTION)
        # index_js = self._find_and_insert(index_js, index, SET_DRM_DATA_RE, "setDrmData")
        # index_js = self._find_and_insert(index_js, index, ENCRYPT_WITH_MD5_RE, "encryptLicenseWithMd5Verifier")
        index_js = self._find_and_insert(index_js, index, SET_CURRENT_LICENSE_RE, "setCurrentLicense")
        index_js = self._find_and_insert(index_js, index, ECRYPT_DECRYPT_BYTES_RE, "ECRYPT_decrypt_bytes")
        index_js = self._find_and_insert(index_js, index, ECRYPT_DECRYPTK_RE, "ECRYPT_decryptk")

        open(self.player_file, "w", encoding="utf-8").write(index_js)

        return True
