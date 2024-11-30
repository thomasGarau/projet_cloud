from pathlib import Path
import json
import base64

import base64

def compresse_file(contenu_original: bytes, extension: str) -> str:
    """
    Compresse un fichier et retourne son contenu compressé encodé en Base64.

    :param contenu_original: Contenu du fichier à compresser (bytes).
    :param extension: Extension du fichier original (str).
    :return: Fichier compressé encodé en Base64 (str).
    """
    # Création du dictionnaire et de l'arbre Huffman
    dico = cree_dictionnaire(contenu_original)
    arbre = cree_arbre_huffman(dico)
    table_codage = genere_table_codage(arbre)

    # Compression
    contenu_encode = encode_fichier(contenu_original, table_codage)
    fichier_assembler = assembler_fichier_comprime(table_codage, contenu_encode, extension)

    # Vérification du type de fichier_assembler
    if not isinstance(fichier_assembler, bytes):
        raise TypeError(f"assembler_fichier_comprime a retourné un type inattendu : {type(fichier_assembler)}")

    # Encodage en Base64
    fichier_base64 = base64.b64encode(fichier_assembler).decode('utf-8')
    print("Chaîne Base64 générée :", fichier_base64[:100]) 

    return fichier_base64

def decompresse_file(fichier_comprime: bytes) -> (bytes, str):
    extension_originale, table_codage, contenu_encode_bytes = desassembler_fichier_comprime(fichier_comprime)
    table_codage_inverse = {v: k for k, v in table_codage.items()}
    contenu_decode = decode_fichier(contenu_encode_bytes, table_codage_inverse)

    return contenu_decode, extension_originale

def cree_dictionnaire(contenu_fichier: bytes) -> dict:
    dictionnaire_frequences = {}
    for octet in contenu_fichier:
        if octet in dictionnaire_frequences:
            dictionnaire_frequences[octet] += 1
        else:
            dictionnaire_frequences[octet] = 1
    return dictionnaire_frequences

class NoeudHuffman:
    def __init__(self, frequence, octet=None, gauche=None, droit=None):
        self.frequence = frequence
        self.octet = octet
        self.gauche = gauche
        self.droit = droit

def cree_arbre_huffman(dictionnaire_frequences):
    noeuds = [NoeudHuffman(freq, octet) for octet, freq in dictionnaire_frequences.items()]
    
    while len(noeuds) > 1:
        noeuds.sort(key=lambda noeud: noeud.frequence)
        gauche = noeuds.pop(0)
        droit = noeuds.pop(0)
        
        noeud_fusionne = NoeudHuffman(gauche.frequence + droit.frequence, gauche=gauche, droit=droit)
        
        noeuds.append(noeud_fusionne)
    
    return noeuds[0]

def genere_table_codage(noeud, chemin_actuel="", table_codage=None):
    if table_codage is None:
        table_codage = {}

    if noeud.octet is not None:
        table_codage[noeud.octet] = chemin_actuel
    
    if noeud.gauche is not None:
        genere_table_codage(noeud.gauche, chemin_actuel + "0", table_codage)
    if noeud.droit is not None:
        genere_table_codage(noeud.droit, chemin_actuel + "1", table_codage)

    return table_codage

def encode_fichier(contenu_fichier, table_codage):
    contenu_encode = ""
    for octet in contenu_fichier:
        contenu_encode += table_codage[octet]
    return contenu_encode

def decode_fichier(contenu_encode: str, table_codage_inverse: dict) -> bytes:
    contenu_decode = bytearray() #""
    code_temp = ""
    for bit in contenu_encode:
        code_temp += str(bit)
        if code_temp in table_codage_inverse:
            octet = table_codage_inverse[code_temp]
            contenu_decode.append(int(octet))
            code_temp = ""
    return bytes(contenu_decode)

def bitstring_to_bytes(s):
    return int(s, 2).to_bytes((len(s) + 7) // 8, byteorder='big')

def assembler_fichier_comprime(table_codage, contenu_encode, extension_originale):
    # Convertir la table de codage en une suite d'octets plus compacte
    table_codage_bytes = encoder_table_codage(table_codage)
    extension_bytes = extension_originale.encode('utf-8')
    taille_extension = len(extension_bytes)

    taille_table_codage = len(table_codage_bytes)
    bits_manquants = (8 - len(contenu_encode) % 8) % 8
    contenu_encode_ajuste = contenu_encode + '0' * bits_manquants
    contenu_encode_bytes = bitstring_to_bytes(contenu_encode_ajuste)

    en_tete = taille_table_codage.to_bytes(4, 'big') + bits_manquants.to_bytes(4, 'big') + taille_extension.to_bytes(4, 'big') + extension_bytes + table_codage_bytes
    fichier_comprime = en_tete + contenu_encode_bytes
    return fichier_comprime

def desassembler_fichier_comprime(fichier_comprime):
    taille_table_codage = int.from_bytes(fichier_comprime[:4], 'big')
    bits_manquants = int.from_bytes(fichier_comprime[4:8], 'big')
    taille_extension = int.from_bytes(fichier_comprime[8:12], 'big')

    debut_extension = 12
    fin_extension = debut_extension + taille_extension
    extension_bytes = fichier_comprime[debut_extension:fin_extension]
    extension_originale = extension_bytes.decode('utf-8')

    debut_table_codage = fin_extension
    fin_table_codage = debut_table_codage + taille_table_codage
    table_codage_bytes = fichier_comprime[debut_table_codage:fin_table_codage]
    table_codage = decoder_table_codage(table_codage_bytes)

    contenu_encode_bytes = fichier_comprime[fin_table_codage:]
    bit_string = ''.join([format(byte, '08b') for byte in contenu_encode_bytes])
    bit_string_sans_padding = bit_string[:-bits_manquants] if bits_manquants > 0 else bit_string

    return extension_originale, table_codage, bit_string_sans_padding

def encoder_table_codage(table_codage):
    result = bytearray()
    for key, value in table_codage.items():
        key_byte = int(key).to_bytes(1, 'big')
        code_length = len(value)
        length_bits = code_length.to_bytes(1, 'big')  # 1 byte pour la longueur
        code_bits = int(value, 2).to_bytes((code_length + 7) // 8, 'big')  # Convertir en bytes
        result.extend(key_byte)
        result.extend(length_bits)
        result.extend(code_bits)  # Ajouter les bits de code
    return bytes(result)


def decoder_table_codage(encoded_data):
    table_codage = {}
    i = 0
    while i < len(encoded_data):
        #on recupere le premier octet qui est la clé
        key = encoded_data[i]
        i += 1
        #on recupére la taille que fait le codage en bits pour la clé
        code_length = encoded_data[i]
        i += 1
        #on recupere le codage en bits en fonction de la taille récupérée
        code_bytes = encoded_data[i:i + (code_length + 7) // 8]
        #on incrémente i du nombre de bits récupérés
        i += (code_length + 7) // 8
        #on tranforme le code de bits en entier puis string pour l'ajouter à la table de codage
        code = int.from_bytes(code_bytes, 'big')
        code_str = format(code, f"0{code_length}b")
        table_codage[key] = code_str
    return table_codage


def affiche_arbre_huffman(noeud, prefix=""):
    if noeud.octet is not None:
        print(f"{prefix}Octet: {noeud.octet}, Fréquence: {noeud.frequence}")
    else:
        print(f"{prefix}Fréquence: {noeud.frequence}")
        if noeud.gauche:
            affiche_arbre_huffman(noeud.gauche, prefix + "0")
        if noeud.droit:
            affiche_arbre_huffman(noeud.droit, prefix + "1")

def test_compression_decompression():
    # Lire le contenu du fichier aide.pdf
    with open(r"C:\Users\thoma\projet\projet_cloud\server\app\services\aide.pdf", "rb") as fichier:
        contenu_original = fichier.read()

    # Compression du fichier
    fichier_comprime = compresse_file(contenu_original, "pdf")

    # Encodage en Base64 pour transmission
    fichier_comprime_base64 = base64.b64encode(fichier_comprime).decode('utf-8')

    # Décodage Base64 avant décompression
    fichier_comprime_decode = base64.b64decode(fichier_comprime_base64)

    # Décompression du fichier
    contenu_decompresse, extension = decompresse_file(fichier_comprime_decode)
    
    # Vérification et affichage
    if contenu_original == contenu_decompresse:
        print("Le test de compression et de décompression a réussi. Le contenu original et décompressé sont identiques.")
    else:
        print("Le test de compression et de décompression a échoué. Il y a une différence entre le contenu original et décompressé.")
    
    # Afficher les 100 premiers octets après décompression
    print("100 premiers octets après décompression :", contenu_decompresse[:500])

def test_cree_dictionnaire():
    contenu_test = b"affbcbecddcdefefdefef"
    resultat_attendu = {97: 1, 98: 2, 99: 3, 100: 4, 101:5, 102:6}  # ASCII de 'a' = 97, 'b' = 98, 'c' = 99
    resultat_obtenu = cree_dictionnaire(contenu_test)
    assert resultat_obtenu == resultat_attendu, "Le dictionnaire de fréquences obtenu ne correspond pas au résultat attendu."

    print("Le test de la fonction cree_dictionnaire a réussi.")

def test_cree_arbre_huffman_complexe():
    dictionnaire_frequences = {
        101: 5,
        116: 3,
        32: 2,
        109: 2,
        111: 2,
        104: 1,
        100: 1,
        105: 1,
        112: 1,
        115: 1,
        99: 1
    }  # 'a': 1, 'b': 2, 'c': 3, 
    arbre_huffman = cree_arbre_huffman(dictionnaire_frequences)
    # La fréquence totale à la racine doit être la somme des fréquences
    assert arbre_huffman.frequence == 20, "La fréquence totale à la racine de l'arbre de Huffman est incorrecte."
    assert arbre_huffman.gauche.frequence == 8, "La fréquence du noeud gauche de la racine de l'arbre de Huffman est incorrecte."
    assert arbre_huffman.gauche.gauche.frequence == 4, "La fréquence du noeud gauche du noeud gauche de la racine de l'arbre de Huffman est incorrecte."
    assert arbre_huffman.gauche.gauche.gauche.frequence == 2, "La fréquence du noeud gauche du noeud gauche du noeud gauche de la racine de l'arbre de Huffman est incorrecte."
    assert arbre_huffman.gauche.gauche.droit.frequence == 2, "La fréquence du noeud droit du noeud gauche du noeud gauche de la racine de l'arbre de Huffman est incorrecte."
    assert arbre_huffman.gauche.droit.frequence == 4, "La fréquence du noeud droit du noeud gauche de la racine de l'arbre de Huffman est incorrecte."
    assert arbre_huffman.gauche.droit.gauche.frequence == 2, "La fréquence du noeud gauche du noeud droit du noeud gauche de la racine de l'arbre de Huffman est incorrecte."
    assert arbre_huffman.gauche.droit.droit.frequence == 2, "La fréquence du noeud droit du noeud droit du noeud gauche de la racine de l'arbre de Huffman est incorrecte."
    assert arbre_huffman.droit.frequence == 12, "La fréquence du noeud droit de la racine de l'arbre de Huffman est incorrecte."
    assert arbre_huffman.droit.gauche.frequence == 5, "La fréquence du noeud gauche du noeud droit de la racine de l'arbre de Huffman est incorrecte."
    assert arbre_huffman.droit.droit.frequence == 7, "La fréquence du noeud droit du noeud droit de la racine de l'arbre de Huffman est incorrecte."
    assert arbre_huffman.droit.droit.gauche.frequence == 3, "La fréquence du noeud gauche du noeud droit du noeud droit de la racine de l'arbre de Huffman est incorrecte."
    assert arbre_huffman.droit.droit.droit.frequence == 4, "La fréquence du noeud droit du noeud droit du noeud droit de la racine de l'arbre de Huffman est incorrecte."
    assert arbre_huffman.droit.droit.droit.gauche.frequence == 2, "La fréquence du noeud gauche du noeud droit du noeud droit du noeud droit de la racine de l'arbre de Huffman est incorrecte."
    assert arbre_huffman.droit.droit.droit.droit.frequence == 2, "La fréquence du noeud droit du noeud droit du noeud droit du noeud droit de la racine de l'arbre de Huffman est incorrecte."


    print("Le test de la fonction cree_arbre_huffman a réussi.")


def test_genere_table_codage():
    # Construction de l'arbre de Huffman basée sur l'exemple donné
    #racine
    racine = NoeudHuffman(frequence=20)
    #gauche
    racine.gauche = NoeudHuffman(frequence=8)

    #gauche gauche
    racine.gauche.gauche = NoeudHuffman(frequence=4)
    racine.gauche.gauche.gauche = NoeudHuffman(frequence=2, octet=111)  # 'o'
    racine.gauche.gauche.droit = NoeudHuffman(frequence=2)
    racine.gauche.gauche.droit.gauche = NoeudHuffman(frequence=1, octet=104)  # 'h'
    racine.gauche.gauche.droit.droit = NoeudHuffman(frequence=1, octet=100)  # 'd'

    #gauche droite
    racine.gauche.droit = NoeudHuffman(frequence=4)
    racine.gauche.droit.gauche = NoeudHuffman(frequence=2)
    racine.gauche.droit.gauche.gauche = NoeudHuffman(frequence=1, octet=105)  # 'i'
    racine.gauche.droit.gauche.droit = NoeudHuffman(frequence=1, octet=112)  # 'p'
    racine.gauche.droit.droit = NoeudHuffman(frequence=2)
    racine.gauche.droit.droit.gauche = NoeudHuffman(frequence=1, octet=115)  # 's'
    racine.gauche.droit.droit.droit = NoeudHuffman(frequence=1, octet=99)  # 'c'

    #droite 
    racine.droit = NoeudHuffman(frequence=12)
    racine.droit.gauche = NoeudHuffman(frequence=5, octet=101)  # 'e'
    racine.droit.droit = NoeudHuffman(frequence=7)
    racine.droit.droit.gauche = NoeudHuffman(frequence=3, octet=116)  # 't'
    racine.droit.droit.droit = NoeudHuffman(frequence=4)
    racine.droit.droit.droit.gauche = NoeudHuffman(frequence=2, octet=32)  # 'espace'
    racine.droit.droit.droit.droit = NoeudHuffman(frequence=2, octet=109)  # 'm'

    # Génération de la table de codage
    table_codage = genere_table_codage(racine)
    
    # Table de codage attendue
    table_attendue = {
        111: "000",   # 'o'
        104: "0010",  # 'h'
        100: "0011",  # 'd'
        105: "0100",  # 'i'
        112: "0101",  # 'p'
        115: "0110",  # 's'
        99:  "0111",  # 'c'
        101: "10",    # 'e'
        116: "110",   # 't'
        32:  "1110",  # 'espace'
        109: "1111"   # 'm'
    }
    
    #Trier les dictionnaires par clé avant de comparer, surtout pour assurer la cohérence en cas de besoin
    obtenu_trie = dict(sorted(table_codage.items()))
    attendu_trie = dict(sorted(table_attendue.items()))
    print("obtenu_trie : ", obtenu_trie)
    print("attendu_trie : ", attendu_trie)

    assert obtenu_trie == attendu_trie, "La table de codage générée ne correspond pas à la table attendue."

    return "Le test de la fonction genere_table_codage a réussi."

def test_encode_table_codage():
    table_codage = {
        111: "000",   # 'o'
        104: "0010",  # 'h'
        100: "0011",  # 'd'
        105: "0100",  # 'i'
    }
    table_bytes = encoder_table_codage(table_codage)
    resultat_attendu = b"\x6f\x03\x00\x68\x04\x02\x64\x04\x03\x69\x04\x04"
    
    print("table_bytes : ", table_bytes)
    print("resultat_attendu : ", resultat_attendu)
    assert table_bytes == resultat_attendu, "La table de codage récupérée ne correspond pas à la table d'origine."

    print("Le test de la fonction encode_table_codage a réussi.")

def test_decode_table_codage():
    resultat_attendu = {
        111: "000",   # 'o'
        104: "0010",  # 'h'
        100: "0011",  # 'd'
        105: "0100",  # 'i'
    }
    table_bytes = b"\x6f\x03\x00\x68\x04\x02\x64\x04\x03\x69\x04\x04"
    table_recuperee = decoder_table_codage(table_bytes)

    print("table_recuperee : ", table_recuperee)
    assert table_recuperee == resultat_attendu, "La table de codage récupérée ne correspond pas à la table d'origine."


def run_test():
    test_compression_decompression()
    test_cree_dictionnaire()
    test_cree_arbre_huffman_complexe()
    test_genere_table_codage()
    test_encode_table_codage()
    test_decode_table_codage()
#run_test()
