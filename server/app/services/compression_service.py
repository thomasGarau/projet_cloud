from pathlib import Path
import json

def compresse_file(contenu_original: bytes, extension: str) -> bytes:
    dico = cree_dictionnaire(contenu_original)
    arbre = cree_arbre_huffman(dico)
    table_codage = genere_table_codage(arbre)
    contenu_encode = encode_fichier(contenu_original, table_codage)
    print("taille contenu_encode sans assemblage entete", len(bitstring_to_bytes(contenu_encode)))
    fichier_assembler = assembler_fichier_comprime(table_codage, contenu_encode, extension)
    return fichier_assembler

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
    table_codage_bytes = json.dumps(table_codage).encode('utf-8')
    extension_bytes = extension_originale.encode('utf-8')
    taille_extension = len(extension_bytes)
    
    taille_table_codage = len(table_codage_bytes)
    bits_manquants = (8 - len(contenu_encode) % 8) % 8
    contenu_encode_ajuste = contenu_encode + '0' * bits_manquants
    contenu_encode_bytes = bitstring_to_bytes(contenu_encode_ajuste)
    
    en_tete = taille_table_codage.to_bytes(4, 'big') + bits_manquants.to_bytes(4, 'big') + taille_extension.to_bytes(4, 'big')
    
    fichier_comprime = en_tete + extension_bytes + table_codage_bytes + contenu_encode_bytes
    return fichier_comprime

def desassembler_fichier_comprime(fichier_comprime):

    taille_table_codage = int.from_bytes(fichier_comprime[:4], 'big')
    bits_manquants = int.from_bytes(fichier_comprime[4:8], 'big')
    taille_extension = int.from_bytes(fichier_comprime[8:12], 'big')
    
    debut_table_codage = 12 + taille_extension
    extension_bytes = fichier_comprime[12:debut_table_codage]
    extension_originale = extension_bytes.decode('utf-8')
    
    fin_table_codage = debut_table_codage + taille_table_codage
    table_codage_bytes = fichier_comprime[debut_table_codage:fin_table_codage]
    table_codage = json.loads(table_codage_bytes.decode('utf-8'))
    
    contenu_encode_bytes = fichier_comprime[fin_table_codage:]
    bit_string = ''.join([format(byte, '08b') for byte in contenu_encode_bytes])
    bit_string_sans_padding = bit_string[:-bits_manquants] if bits_manquants > 0 else bit_string
    
    return extension_originale, table_codage, bit_string_sans_padding


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
    contenu_original = b"ceci est un test trop jolie sympa tout ca tout ca mais je pense que ca commence a me casser les couilles moi tout ca c'est connerie de huffman et de t en trop ."
    dico = cree_dictionnaire(contenu_original)
    arbre = cree_arbre_huffman(dico)
    table_codage = genere_table_codage(arbre)
    
    contenu_encode = encode_fichier(contenu_original, table_codage)
    fichier_comprime = assembler_fichier_comprime(table_codage, contenu_encode, "txt")
    extension, table_codage_recuperee, contenu_encode_recupere = desassembler_fichier_comprime(fichier_comprime)
    contenu_encode_bytes = bitstring_to_bytes(contenu_encode_recupere)
    contenu_decompresse = decode_fichier(contenu_encode_bytes, {v: int(k) for k, v in table_codage_recuperee.items()})
    if contenu_original == contenu_decompresse:
        print("Le test de compression et de décompression a réussi. Le contenu original et décompressé sont identiques.")
    else:
        print("Le test de compression et de décompression a échoué. Il y a une différence entre le contenu original et décompressé.")
    print("taille contenu original : ", len(contenu_original), "taille contenu encoder : ", len(contenu_encode), "taux de compression : ", (1 - len(contenu_encode) / len(contenu_original)) * 100, "%")

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

def run_test():
    #test_compression_decompression()
    test_cree_dictionnaire()
    test_cree_arbre_huffman_complexe()
    test_genere_table_codage()

run_test()
