import platform
import subprocess


def is_certificate_installed(cert_name = 'mitmproxy'):
    if platform.system() == 'Windows':
        import wincertstore

        stores = ["MY", "ROOT", "CA"]
        for store_name in stores:
            with wincertstore.CertSystemStore(store_name) as store:
                for cert in store.itercerts():
                    name = cert.get_name()
                    if name == cert_name:
                        return True
        return False
    elif platform.system() == 'Darwin':
        try:
            result = subprocess.run(['security', 'find-certificate', '-c', cert_name], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            raise NotImplementedError("此系统中未找到 security 命令")
    else:
        raise NotImplementedError(f"暂不支持该系统: {platform.system()}")
