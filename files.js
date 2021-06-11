
  var Module = typeof Module !== 'undefined' ? Module : {};
  
  if (!Module.expectedDataFileDownloads) {
    Module.expectedDataFileDownloads = 0;
  }
  Module.expectedDataFileDownloads++;
  (function() {
   var loadPackage = function(metadata) {
  
      var PACKAGE_PATH;
      if (typeof window === 'object') {
        PACKAGE_PATH = window['encodeURIComponent'](window.location.pathname.toString().substring(0, window.location.pathname.toString().lastIndexOf('/')) + '/');
      } else if (typeof location !== 'undefined') {
        // worker
        PACKAGE_PATH = encodeURIComponent(location.pathname.toString().substring(0, location.pathname.toString().lastIndexOf('/')) + '/');
      } else {
        throw 'using preloaded data can only be done on a web page or in a web worker';
      }
      var PACKAGE_NAME = 'files.data';
      var REMOTE_PACKAGE_BASE = 'files.data';
      if (typeof Module['locateFilePackage'] === 'function' && !Module['locateFile']) {
        Module['locateFile'] = Module['locateFilePackage'];
        err('warning: you defined Module.locateFilePackage, that has been renamed to Module.locateFile (using your locateFilePackage for now)');
      }
      var REMOTE_PACKAGE_NAME = Module['locateFile'] ? Module['locateFile'](REMOTE_PACKAGE_BASE, '') : REMOTE_PACKAGE_BASE;
    
      var REMOTE_PACKAGE_SIZE = metadata['remote_package_size'];
      var PACKAGE_UUID = metadata['package_uuid'];
    
      function fetchRemotePackage(packageName, packageSize, callback, errback) {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', packageName, true);
        xhr.responseType = 'arraybuffer';
        xhr.onprogress = function(event) {
          var url = packageName;
          var size = packageSize;
          if (event.total) size = event.total;
          if (event.loaded) {
            if (!xhr.addedTotal) {
              xhr.addedTotal = true;
              if (!Module.dataFileDownloads) Module.dataFileDownloads = {};
              Module.dataFileDownloads[url] = {
                loaded: event.loaded,
                total: size
              };
            } else {
              Module.dataFileDownloads[url].loaded = event.loaded;
            }
            var total = 0;
            var loaded = 0;
            var num = 0;
            for (var download in Module.dataFileDownloads) {
            var data = Module.dataFileDownloads[download];
              total += data.total;
              loaded += data.loaded;
              num++;
            }
            total = Math.ceil(total * Module.expectedDataFileDownloads/num);
            if (Module['setStatus']) Module['setStatus']('Downloading data... (' + loaded + '/' + total + ')');
          } else if (!Module.dataFileDownloads) {
            if (Module['setStatus']) Module['setStatus']('Downloading data...');
          }
        };
        xhr.onerror = function(event) {
          throw new Error("NetworkError for: " + packageName);
        }
        xhr.onload = function(event) {
          if (xhr.status == 200 || xhr.status == 304 || xhr.status == 206 || (xhr.status == 0 && xhr.response)) { // file URLs can return 0
            var packageData = xhr.response;
            callback(packageData);
          } else {
            throw new Error(xhr.statusText + " : " + xhr.responseURL);
          }
        };
        xhr.send(null);
      };

      function handleError(error) {
        console.error('package error:', error);
      };
    
    function runWithFS() {
  
      function assert(check, msg) {
        if (!check) throw msg + new Error().stack;
      }
  Module['FS_createPath']("/", "scummvm", true, true);
Module['FS_createPath']("/scummvm", "shaders", true, true);

          /** @constructor */
          function DataRequest(start, end, audio) {
            this.start = start;
            this.end = end;
            this.audio = audio;
          }
          DataRequest.prototype = {
            requests: {},
            open: function(mode, name) {
              this.name = name;
              this.requests[name] = this;
              Module['addRunDependency']('fp ' + this.name);
            },
            send: function() {},
            onload: function() {
              var byteArray = this.byteArray.subarray(this.start, this.end);
              this.finish(byteArray);
            },
            finish: function(byteArray) {
              var that = this;
      
          Module['FS_createDataFile'](this.name, null, byteArray, true, true, true); // canOwn this data in the filesystem, it is a slide into the heap that will never change
          Module['removeRunDependency']('fp ' + that.name);
  
              this.requests[this.name] = null;
            }
          };
      
              var files = metadata['files'];
              for (var i = 0; i < files.length; ++i) {
                new DataRequest(files[i]['start'], files[i]['end'], files[i]['audio']).open('GET', files[i]['filename']);
              }
      
        
        var indexedDB;
        if (typeof window === 'object') {
          indexedDB = window.indexedDB || window.mozIndexedDB || window.webkitIndexedDB || window.msIndexedDB;
        } else if (typeof location !== 'undefined') {
          // worker
          indexedDB = self.indexedDB;
        } else {
          throw 'using IndexedDB to cache data can only be done on a web page or in a web worker';
        }
        var IDB_RO = "readonly";
        var IDB_RW = "readwrite";
        var DB_NAME = "EM_PRELOAD_CACHE";
        var DB_VERSION = 1;
        var METADATA_STORE_NAME = 'METADATA';
        var PACKAGE_STORE_NAME = 'PACKAGES';
        function openDatabase(callback, errback) {
          try {
            var openRequest = indexedDB.open(DB_NAME, DB_VERSION);
          } catch (e) {
            return errback(e);
          }
          openRequest.onupgradeneeded = function(event) {
            var db = event.target.result;

            if(db.objectStoreNames.contains(PACKAGE_STORE_NAME)) {
              db.deleteObjectStore(PACKAGE_STORE_NAME);
            }
            var packages = db.createObjectStore(PACKAGE_STORE_NAME);

            if(db.objectStoreNames.contains(METADATA_STORE_NAME)) {
              db.deleteObjectStore(METADATA_STORE_NAME);
            }
            var metadata = db.createObjectStore(METADATA_STORE_NAME);
          };
          openRequest.onsuccess = function(event) {
            var db = event.target.result;
            callback(db);
          };
          openRequest.onerror = function(error) {
            errback(error);
          };
        };

        // This is needed as chromium has a limit on per-entry files in IndexedDB
        // https://cs.chromium.org/chromium/src/content/renderer/indexed_db/webidbdatabase_impl.cc?type=cs&sq=package:chromium&g=0&l=177
        // https://cs.chromium.org/chromium/src/out/Debug/gen/third_party/blink/public/mojom/indexeddb/indexeddb.mojom.h?type=cs&sq=package:chromium&g=0&l=60
        // We set the chunk size to 64MB to stay well-below the limit
        var CHUNK_SIZE = 64 * 1024 * 1024;

        function cacheRemotePackage(
          db,
          packageName,
          packageData,
          packageMeta,
          callback,
          errback
        ) {
          var transactionPackages = db.transaction([PACKAGE_STORE_NAME], IDB_RW);
          var packages = transactionPackages.objectStore(PACKAGE_STORE_NAME);
          var chunkSliceStart = 0;
          var nextChunkSliceStart = 0;
          var chunkCount = Math.ceil(packageData.byteLength / CHUNK_SIZE);
          var finishedChunks = 0;
          for (var chunkId = 0; chunkId < chunkCount; chunkId++) {
            nextChunkSliceStart += CHUNK_SIZE;
            var putPackageRequest = packages.put(
              packageData.slice(chunkSliceStart, nextChunkSliceStart),
              'package/' + packageName + '/' + chunkId
            );
            chunkSliceStart = nextChunkSliceStart;
            putPackageRequest.onsuccess = function(event) {
              finishedChunks++;
              if (finishedChunks == chunkCount) {
                var transaction_metadata = db.transaction(
                  [METADATA_STORE_NAME],
                  IDB_RW
                );
                var metadata = transaction_metadata.objectStore(METADATA_STORE_NAME);
                var putMetadataRequest = metadata.put(
                  {
                    'uuid': packageMeta.uuid,
                    'chunkCount': chunkCount
                  },
                  'metadata/' + packageName
                );
                putMetadataRequest.onsuccess = function(event) {
                  callback(packageData);
                };
                putMetadataRequest.onerror = function(error) {
                  errback(error);
                };
              }
            };
            putPackageRequest.onerror = function(error) {
              errback(error);
            };
          }
        }

        /* Check if there's a cached package, and if so whether it's the latest available */
        function checkCachedPackage(db, packageName, callback, errback) {
          var transaction = db.transaction([METADATA_STORE_NAME], IDB_RO);
          var metadata = transaction.objectStore(METADATA_STORE_NAME);
          var getRequest = metadata.get('metadata/' + packageName);
          getRequest.onsuccess = function(event) {
            var result = event.target.result;
            if (!result) {
              return callback(false, null);
            } else {
              return callback(PACKAGE_UUID === result['uuid'], result);
            }
          };
          getRequest.onerror = function(error) {
            errback(error);
          };
        }

        function fetchCachedPackage(db, packageName, metadata, callback, errback) {
          var transaction = db.transaction([PACKAGE_STORE_NAME], IDB_RO);
          var packages = transaction.objectStore(PACKAGE_STORE_NAME);

          var chunksDone = 0;
          var totalSize = 0;
          var chunkCount = metadata['chunkCount'];
          var chunks = new Array(chunkCount);

          for (var chunkId = 0; chunkId < chunkCount; chunkId++) {
            var getRequest = packages.get('package/' + packageName + '/' + chunkId);
            getRequest.onsuccess = function(event) {
              // If there's only 1 chunk, there's nothing to concatenate it with so we can just return it now
              if (chunkCount == 1) {
                callback(event.target.result);
              } else {
                chunksDone++;
                totalSize += event.target.result.byteLength;
                chunks.push(event.target.result);
                if (chunksDone == chunkCount) {
                  if (chunksDone == 1) {
                    callback(event.target.result);
                  } else {
                    var tempTyped = new Uint8Array(totalSize);
                    var byteOffset = 0;
                    for (var chunkId in chunks) {
                      var buffer = chunks[chunkId];
                      tempTyped.set(new Uint8Array(buffer), byteOffset);
                      byteOffset += buffer.byteLength;
                      buffer = undefined;
                    }
                    chunks = undefined;
                    callback(tempTyped.buffer);
                    tempTyped = undefined;
                  }
                }
              }
            };
            getRequest.onerror = function(error) {
              errback(error);
            };
          }
        }
      
      function processPackageData(arrayBuffer) {
        assert(arrayBuffer, 'Loading data file failed.');
        assert(arrayBuffer instanceof ArrayBuffer, 'bad input to processPackageData');
        var byteArray = new Uint8Array(arrayBuffer);
        var curr;
        
          // Reuse the bytearray from the XHR as the source for file reads.
          DataRequest.prototype.byteArray = byteArray;
    
            var files = metadata['files'];
            for (var i = 0; i < files.length; ++i) {
              DataRequest.prototype.requests[files[i].filename].onload();
            }
                Module['removeRunDependency']('datafile_files.data');

      };
      Module['addRunDependency']('datafile_files.data');
    
      if (!Module.preloadResults) Module.preloadResults = {};
    
        function preloadFallback(error) {
          console.error(error);
          console.error('falling back to default preload behavior');
          fetchRemotePackage(REMOTE_PACKAGE_NAME, REMOTE_PACKAGE_SIZE, processPackageData, handleError);
        };

        openDatabase(
          function(db) {
            checkCachedPackage(db, PACKAGE_PATH + PACKAGE_NAME,
              function(useCached, metadata) {
                Module.preloadResults[PACKAGE_NAME] = {fromCache: useCached};
                if (useCached) {
                  fetchCachedPackage(db, PACKAGE_PATH + PACKAGE_NAME, metadata, processPackageData, preloadFallback);
                } else {
                  fetchRemotePackage(REMOTE_PACKAGE_NAME, REMOTE_PACKAGE_SIZE,
                    function(packageData) {
                      cacheRemotePackage(db, PACKAGE_PATH + PACKAGE_NAME, packageData, {uuid:PACKAGE_UUID}, processPackageData,
                        function(error) {
                          console.error(error);
                          processPackageData(packageData);
                        });
                    }
                  , preloadFallback);
                }
              }
            , preloadFallback);
          }
        , preloadFallback);

        if (Module['setStatus']) Module['setStatus']('Downloading...');
      
    }
    if (Module['calledRun']) {
      runWithFS();
    } else {
      if (!Module['preRun']) Module['preRun'] = [];
      Module["preRun"].push(runWithFS); // FS is not initialized yet, wait for it
    }
  
   }
   loadPackage({"files": [{"filename": "/scummvm/residualvm.zip", "start": 0, "end": 53254, "audio": 0}, {"filename": "/scummvm/queen.tbl", "start": 53254, "end": 1153759, "audio": 0}, {"filename": "/scummvm/grim-patch.lab", "start": 1153759, "end": 1163049, "audio": 0}, {"filename": "/scummvm/lure.dat", "start": 1163049, "end": 1932169, "audio": 0}, {"filename": "/scummvm/monkey4-patch.m4b", "start": 1932169, "end": 1935159, "audio": 0}, {"filename": "/scummvm/encoding.dat", "start": 1935159, "end": 2026037, "audio": 0}, {"filename": "/scummvm/scummremastered.zip", "start": 2026037, "end": 2119541, "audio": 0}, {"filename": "/scummvm/macgui.dat", "start": 2119541, "end": 2134027, "audio": 0}, {"filename": "/scummvm/scummclassic.zip", "start": 2134027, "end": 2160177, "audio": 0}, {"filename": "/scummvm/translations.dat", "start": 2160177, "end": 3746730, "audio": 0}, {"filename": "/scummvm/drascula.dat", "start": 3746730, "end": 4006349, "audio": 0}, {"filename": "/scummvm/fonts.dat", "start": 4006349, "end": 31342947, "audio": 0}, {"filename": "/scummvm/sky.cpt", "start": 31342947, "end": 31762374, "audio": 0}, {"filename": "/scummvm/scummmodern.zip", "start": 31762374, "end": 31835978, "audio": 0}, {"filename": "/scummvm/shaders/grim_primitive.fragment", "start": 31835978, "end": 31836053, "audio": 0}, {"filename": "/scummvm/shaders/emi_actorlights.vertex", "start": 31836053, "end": 31839137, "audio": 0}, {"filename": "/scummvm/shaders/emi_actor.fragment", "start": 31839137, "end": 31839565, "audio": 0}, {"filename": "/scummvm/shaders/grim_shadowplane.fragment", "start": 31839565, "end": 31839627, "audio": 0}, {"filename": "/scummvm/shaders/grim_background.fragment", "start": 31839627, "end": 31839730, "audio": 0}, {"filename": "/scummvm/shaders/grim_text.fragment", "start": 31839730, "end": 31839872, "audio": 0}, {"filename": "/scummvm/shaders/grim_emerg.fragment", "start": 31839872, "end": 31840014, "audio": 0}, {"filename": "/scummvm/shaders/grim_dim.fragment", "start": 31840014, "end": 31840192, "audio": 0}, {"filename": "/scummvm/shaders/grim_smush.vertex", "start": 31840192, "end": 31840569, "audio": 0}, {"filename": "/scummvm/shaders/grim_dim.vertex", "start": 31840569, "end": 31840868, "audio": 0}, {"filename": "/scummvm/shaders/grim_actorlights.fragment", "start": 31840868, "end": 31841827, "audio": 0}, {"filename": "/scummvm/shaders/emi_actorlights.fragment", "start": 31841827, "end": 31842255, "audio": 0}, {"filename": "/scummvm/shaders/emi_sprite.vertex", "start": 31842255, "end": 31843377, "audio": 0}, {"filename": "/scummvm/shaders/grim_background.vertex", "start": 31843377, "end": 31843757, "audio": 0}, {"filename": "/scummvm/shaders/grim_actorlights.vertex", "start": 31843757, "end": 31846498, "audio": 0}, {"filename": "/scummvm/shaders/grim_smush.fragment", "start": 31846498, "end": 31846753, "audio": 0}, {"filename": "/scummvm/shaders/emi_sprite.fragment", "start": 31846753, "end": 31847181, "audio": 0}, {"filename": "/scummvm/shaders/grim_primitive.vertex", "start": 31847181, "end": 31847429, "audio": 0}, {"filename": "/scummvm/shaders/emi_background.vertex", "start": 31847429, "end": 31847565, "audio": 0}, {"filename": "/scummvm/shaders/grim_shadowplane.vertex", "start": 31847565, "end": 31847742, "audio": 0}, {"filename": "/scummvm/shaders/grim_actor.vertex", "start": 31847742, "end": 31848947, "audio": 0}, {"filename": "/scummvm/shaders/emi_dimplane.vertex", "start": 31848947, "end": 31849153, "audio": 0}, {"filename": "/scummvm/shaders/grim_emerg.vertex", "start": 31849153, "end": 31849557, "audio": 0}, {"filename": "/scummvm/shaders/grim_actor.fragment", "start": 31849557, "end": 31850516, "audio": 0}, {"filename": "/scummvm/shaders/grim_text.vertex", "start": 31850516, "end": 31850792, "audio": 0}, {"filename": "/scummvm/shaders/emi_dimplane.fragment", "start": 31850792, "end": 31850874, "audio": 0}, {"filename": "/scummvm/shaders/emi_actor.vertex", "start": 31850874, "end": 31852141, "audio": 0}, {"filename": "/scummvm/shaders/emi_background.fragment", "start": 31852141, "end": 31852248, "audio": 0}], "remote_package_size": 31852248, "package_uuid": "a054cce8-a26b-4484-917b-2cd7ce7d2173"});
  
  })();
  