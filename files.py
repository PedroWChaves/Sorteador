import json
import os

def default_data():
    return {
        "configs": {
            "profile": "account-circle",
            "color": "Yellow",
            "color_hue": "300",
            "accent": "LightBlue",
            "accent_hue": "400",
            "theme": "Dark",
            "time_format": "%d/%m - %Hh%M",
            "num_meus_sorteios": "10",
            "autosave": True
        },
        "ultimos": [],
        "tabs": [
            {
                "title": "Números",
                "tipo": "Numero",
                "minimum": "1",
                "maximum": "100",
                "sorteado": ""
            }
        ]
    }

def check_json_file(app):
    for key, value in default_data()["configs"].items():
        if not key in app.data["configs"]:
            app.data["configs"][key] = value

def load_json(path, file):
    error = False
    try:
        with open(path + file, "r") as f:
            data = json.load(f)

    except (FileNotFoundError, json.decoder.JSONDecodeError) as e:
        data = default_data()
        error = e

    return (data, error)

def save_json(data, path, file):
    with open(path + file, "w") as f:
        json.dump(data, f, indent=4)

    #print("json salvo!") # ABRIR DIALOGO OU SNACKBAR PARA AVISAR QUE FOI SALVO COM SUCESSO
                          # OU RETORNAR VERDADEIRO

def reset_json(path, file):
    save_json(default_data(), path, file)

def delete_json(path, file):
    if not os.path.exists(path + file):
      return

    os.remove(path + file)

def rename_json(path, old_name, new_name): # TESTAR
    if not os.path.exists(path + old_name):
        return

    if os.path.exists(path + new_name):
        for n in range(1, len([name for name in os.listdir(path)])):
            try_name = f"{path}{new_name.split('.')[0]} ({n}).json"

            if not os.path.exists(try_name):
                os.rename(path + new_name, try_name)
                break

    os.rename(path + old_name, path + new_name)

