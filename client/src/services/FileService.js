export const getFileIcons = () => {
    return {
      pdf: process.env.PUBLIC_URL + '/extension-icons/icone-pdf.png',
      docx: process.env.PUBLIC_URL + '/extension-icons/icone-word.png',
      jpg: process.env.PUBLIC_URL + '/extension-icons/icone-jpg.png',
      png: process.env.PUBLIC_URL + '/extension-icons/icone-png.png',
      txt: process.env.PUBLIC_URL + '/extension-icons/icone-txt.png',
      webp: process.env.PUBLIC_URL + '/extension-icons/icone-webp.png',
    };
  };
  
  export const getMimeTypes = () => {
    return {
      jpg: 'image/jpeg',
      jpeg: 'image/jpeg',
      png: 'image/png',
      doc: 'application/msword',
      docx: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      pdf: 'application/pdf',
      txt: 'text/plain',
      webp: 'image/webp',
      '': 'application/octet-stream'
    };
  };
  