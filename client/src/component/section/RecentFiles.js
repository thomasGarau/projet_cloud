import React from 'react';
import { useFileService } from '../../API/FileServiceAPI';
import FileList from './FileList';

const Recent = ({ openFile, handleOpenRenameModal, handleOpenDeleteModal, handleOpenShareModal }) => {
  const { fetchRecentUserFilesInfo } = useFileService();

  return (
    <FileList
      fetchFilesFunction={fetchRecentUserFilesInfo}
      openFile={openFile}
      handleOpenRenameModal={handleOpenRenameModal}
      handleOpenDeleteModal={handleOpenDeleteModal}
      handleOpenShareModal={handleOpenShareModal}
      isSharedFile={false}
      tableTitle="Fichiers Récents"
    />
  );
};

export default Recent;
