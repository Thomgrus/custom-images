#!/usr/bin/env python3
import argparse
from ruamel.yaml import YAML
import os

def update_yaml(catalog_file, action, yaml_file='catalog-info.yaml'):
  yaml = YAML()
  yaml.preserve_quotes = True
  yaml.indent(mapping=2, sequence=4, offset=2)

  # Vérification de l'existence du fichier
  if not os.path.exists(yaml_file):
    return "Le fichier de Location n'existe pas."

  # Vérification du format YAML
  try:
    with open(yaml_file, 'r') as file:
      data = yaml.load(file)
  except Exception as e:
    return f"Erreur lors du chargement du fichier de Location YAML : {e}"

  message = ""

  # Construction de la cible
  target_path = f'./{catalog_file}'

  if action == 'add':
    if target_path not in data['spec']['targets']:
      data['spec']['targets'].append(target_path)
      with open(yaml_file, 'w') as file:
          yaml.dump(data, file)

      if not os.path.exists(target_path):
        message += f"Warning: le fichier {target_path} à ajouter n'existe pas\n"

      message += "Élément ajouté avec succès.\n"
    else:
      message += "L'élément existe déjà. Aucune modification apportée.\n"
  elif action == 'remove':
    if target_path in data['spec']['targets']:
      data['spec']['targets'].remove(target_path)
      with open(yaml_file, 'w') as file:
        yaml.dump(data, file)
    else:
      message += "Warning: le fichier n'était pas présent dans le catalogue location\n"
    # Suppression du fichier cible si celui-ci existe
    if os.path.exists(target_path):
      os.remove(target_path)
    message += "Élément et fichier cible supprimés avec succès.\n"
  return message

if __name__ == "__main__":
  parser = argparse.ArgumentParser(prog="catalog-location-manager", description="Gère les éléments dans spec.targets d'un fichier YAML")
  parser.add_argument('action', choices=['add', 'remove'], help="Action à effectuer : ajouter ou supprimer un élément")
  parser.add_argument('catalog_file', type=str, help="Filepath du catalogue à gérer dans spec.targets")
  args = parser.parse_args()
  message = update_yaml(args.catalog_file, args.action)
  print(message)
