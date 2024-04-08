import React from 'react';
import { useFileService } from '../../API/FileServiceAPI';
import FileList from './FileList';

const Recent = ({ openFile, handleOpenRenameModal, handleOpenDeleteModal, handleOpenShareModal }) => {
  const { fetchSharedWithMeFiles } = useFileService();

  return (
    <FileList
      fetchFilesFunction={fetchSharedWithMeFiles}
      openFile={openFile}
      handleOpenRenameModal={handleOpenRenameModal}
      handleOpenDeleteModal={handleOpenDeleteModal}
      handleOpenShareModal={handleOpenShareModal}
      isSharedFile={true}
      tableTitle="Fichiers Partagés avec moi"
    />
  );
};

export default Recent;
