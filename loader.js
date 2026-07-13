
      const getProjectData = (function() {
        const storage = scaffolding.storage;
        storage.onprogress = (total, loaded) => {
          setProgress(interpolate(0.75, 0.98, loaded / total));
        };
        
        let zip;
        // Allow zip to be GC'd after project loads
        vm.runtime.on('PROJECT_LOADED', () => (zip = null));
        const findFileInZip = (path) => zip.file(path) || zip.file(new RegExp("^([^/]*/)?" + path + "$"))[0];
        storage.addHelper({
          load: (assetType, assetId, dataFormat) => {
            if (!zip) {
              throw new Error('Zip is not loaded or has been closed');
            }
            const path = assetId + '.' + dataFormat;
            const file = findFileInZip(path);
            if (!file) {
              console.error('Asset is not in zip: ' + path);
              return Promise.resolve(null);
            }
            return file
              .async('uint8array')
              .then((data) => storage.createAsset(assetType, dataFormat, data, assetId));
          }
        });
        return () => (() => {
        const buffer = projectDecodeBuffer;
        projectDecodeBuffer = null; // Allow GC
        return Promise.resolve(new Uint8Array(buffer, 0, 36485721));
      })().then(async (data) => {
          zip = await Scaffolding.JSZip.loadAsync(data);
          const file = findFileInZip('project.json');
          if (!file) {
            throw new Error('project.json is not in zip');
          }
          return file.async('arraybuffer');
        });
      })();
    

    const run = async () => {
      const projectData = await getProjectData();
      await scaffolding.loadProject(projectData);
      setProgress(1);
      loadingScreen.hidden = true;
      if (true) {
        scaffolding.start();
      } else {
        launchScreen.hidden = false;
        launchScreen.addEventListener('click', () => {
          launchScreen.hidden = true;
          scaffolding.start();
        });
        launchScreen.focus();
      }
    };
    run().catch(handleError);
  