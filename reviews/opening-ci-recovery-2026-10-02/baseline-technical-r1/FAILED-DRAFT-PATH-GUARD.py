def safe_path(name):
    p = PurePosixPath(name)
    need(isinstance(name, str) and 0 < len(name) <= 240 and not p.is_absolute()
         and name == str(p) and all(x not in ("", ".", "..") for x in p.parts)
         and "\\" not in name and "\x00" not in name, "noncanonical path")
    return p
