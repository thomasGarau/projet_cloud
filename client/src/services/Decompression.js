// Fonction principale pour décompresser le fichier
export function decompresseFile(fichierComprime) {
    const { extensionOriginale, tableCodage, contenuEncode } = desassemblerFichierComprime(fichierComprime);

    const tableCodageInverse = invertTableCodage(tableCodage);

    // Décodage du contenu
    const contenuDecodeBytes = decodeFichier(contenuEncode, tableCodageInverse);

    // Utiliser TextDecoder pour obtenir une chaîne avec l'encodage correct
    const textDecoder = new TextDecoder('utf-8');
    const contenuDecodeString = textDecoder.decode(contenuDecodeBytes);

    console.log("Contenu décodé (client) :", contenuDecodeString);

    return { contenuDecode: contenuDecodeString, extensionOriginale };
}
// Fonction pour désassembler le fichier compressé
function desassemblerFichierComprime(fichierComprime) {
    const dataView = new DataView(fichierComprime);
    let offset = 0;

    const tailleTableCodage = dataView.getUint32(offset);
    offset += 4;

    const bitsManquants = dataView.getUint32(offset);
    offset += 4;

    const tailleExtension = dataView.getUint32(offset);
    offset += 4;

    const extensionBytes = new Uint8Array(fichierComprime, offset, tailleExtension);
    offset += tailleExtension;
    const extensionOriginale = new TextDecoder().decode(extensionBytes);

    const tableCodageBytes = new Uint8Array(fichierComprime, offset, tailleTableCodage);
    offset += tailleTableCodage;
    const tableCodage = decoderTableCodage(tableCodageBytes);

    const contenuEncodeBytes = new Uint8Array(fichierComprime, offset);
    const bitString = Array.from(contenuEncodeBytes)
        .map(byte => byte.toString(2).padStart(8, '0'))
        .join('');
    const bitStringSansPadding = bitsManquants > 0 ? bitString.slice(0, -bitsManquants) : bitString;

    return { extensionOriginale, tableCodage, contenuEncode: bitStringSansPadding };
}

// Fonction pour décoder la table de codage
function decoderTableCodage(encodedData) {
    const tableCodage = {};
    let i = 0;
    while (i < encodedData.length) {
        const key = encodedData[i++];
        const codeLength = encodedData[i++];
        const codeBytes = encodedData.slice(i, i + Math.ceil(codeLength / 8));
        i += Math.ceil(codeLength / 8);
        const code = Array.from(codeBytes)
            .map(byte => byte.toString(2).padStart(8, '0'))
            .join('');
        tableCodage[key] = code.slice(-codeLength);
    }
    return tableCodage;
}

// Fonction pour inverser la table de codage
function invertTableCodage(tableCodage) {
    const invertedTable = {};
    for (const [key, value] of Object.entries(tableCodage)) {
        invertedTable[value] = String.fromCharCode(key);
    }
    return invertedTable;
}

// Fonction pour décoder les bits en contenu
function decodeFichier(bitString, tableCodageInverse) {
    let currentCode = '';
    const result = [];

    for (const bit of bitString) {
        currentCode += bit;
        if (tableCodageInverse[currentCode]) {
            const byteValue = tableCodageInverse[currentCode].charCodeAt(0); // Assurez-vous de retourner un entier
            result.push(byteValue);
            currentCode = '';
        }
    }

    return new Uint8Array(result); // Retourne un tableau d'octets
}
