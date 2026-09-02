import hashlib
usuarios = {
    "usuario1@gmail.com": {
        "email": "usuario1@gmail.com",
        "password": "nube#47sol",
        "plataformas": {
            "instagram": {
                "email": "usuario1_ig@gmail.com",
                "password": "Ig8Luna92"
            },
            "facebook": {
                "email": "usuario1_fb@gmail.com",
                "password": "Fb31MarAzul"
            },
            "tiktok": {
                "email": "usuario1_tt@gmail.com",
                "password": "Tk72Rayo15"
            },
            "x": {
                "email": "usuario1_x@gmail.com",
                "password": "XX54Estrella"
            },
            "youtube": {
                "email": "usuario1_yt@gmail.com",
                "password": "Yt296SolXube"
            }
        }
    },

    "usuario2@gmail.com": {
        "email": "usuario2@gmail.com",
        "password": "Bosque#82Luz",
        "plataformas": {
            "instagram": {
                "email": "usuario2_ig@gmail.com",
                "password": "Ig#45RioVerde"
            },
            "facebook": {
                "email": "usuario2_fb@gmail.com",
                "password": "Fb31MarAzul"
            },
            "tiktok": {
                "email": "usuario2_tt@gmail.com",
                "password": "Tk72Rayo15"
            },
            "x": {
                "email": "usuario2_x@gmail.com",
                "password": "XX54Estrella"
            },
            "youtube": {
                "email": "usuario2_yt@gmail.com",
                "password": "Yt296SolXube"
            }
        }
    },

    "usuario3@gmail.com": {
        "email": "usuario3@gmail.com",
        "password": "Rayo#39Mar",
        "plataformas": {
            "instagram": {
                "email": "usuario3_ig@gmail.com",
                "password": "Ig#61Cielo"
            },
            "facebook": {
                "email": "usuario3_fb@gmail.com",
                "password": "Fb#84Bosque"
            },
            "tiktok": {
                "email": "usuario3_tt@gmail.com",
                "password": "Tk#25Estrella"
            },
            "x": {
                "email": "usuario3_x@gmail.com",
                "password": "X#97Nube"
            },
            "youtube": {
                "email": "usuario3_yt@gmail.com",
                "password": "Yt#43Luna"
            }
        }
    },

    "usuario4@gmail.com": {
        "email": "usuario4@gmail.com",
        "password": "Luna#56Rayo",
        "plataformas": {
            "instagram": {
                "email": "usuario4_ig@gmail.com",
                "password": "Ig#32Sol"
            },
            "facebook": {
                "email": "usuario4_fb@gmail.com",
                "password": "Fb#75Cielo"
            },
            "tiktok": {
                "email": "usuario4_tt@gmail.com",
                "password": "Tk#48Mar"
            },
            "x": {
                "email": "usuario4_x@gmail.com",
                "password": "X#16Bosque"
            },
            "youtube": {
                "email": "usuario4_yt@gmail.com",
                "password": "Yt#89Rayo"
            }
        }
    }
}

def validar_usuario(usuario, contraseña):
    
    if usuario in usuarios and usuarios[usuario]["password"] == contraseña:
        return True
    else:
        return False
def obtener_contraseñas(usuario):
    if usuario in usuarios:
        return usuarios[usuario]["plataformas"]
    else:
        return None