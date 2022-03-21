// based on https://github.com/gzuidhof/starboard-python/blob/867df3a341beed6ffc7c2ff8b80b1394982ce605/src/worker/emscripten-fs.ts
// see also
// https://github.com/jvilk/BrowserFS/blob/master/src/generic/emscripten_fs.ts
// https://github.com/emscripten-core/emscripten/blob/main/src/library_nodefs.js
// https://github.com/emscripten-core/emscripten/blob/main/src/library_memfs.js
// https://github.com/emscripten-core/emscripten/blob/main/src/library_workerfs.js
// https://github.com/curiousdannii/emglken/blob/master/src/emglkenfs.js
const DIR_MODE = 16895; // 040777
const FILE_MODE = 33206; // 100666
const SEEK_SET = 0;
const SEEK_CUR = 1;
const SEEK_END = 2;
const DEBUG = false
const encoder = new TextEncoder();
const decoder = new TextDecoder("utf-8");
function _split_path(p) {
    const dirpath = p.substr(0, p.lastIndexOf("/"));
    const itemname = p.substr(dirpath.length + (dirpath === "/" ? 0 : 1));
    return [dirpath, itemname];
}

// TODO: We should get these from Emscripten - see https://github.com/emscripten-core/emscripten/issues/10061 and https://github.com/emscripten-core/emscripten/issues/14783
var ERRNO_CODES = {
    EPERM: 1, // Operation not permitted
    ENOENT: 2, // No such file or directory
    EINVAL: 22 // I©nvalid argument
};
function logger(path, message) {
    if (DEBUG) {
        console.log(path + ": " + message)
    }
}
export class ScummvmFS {
    constructor(FS, _url) {
        this.node_ops = {};
        this.stream_ops = {};
        this.FS = FS;

        var req = new XMLHttpRequest(); // a new request
        req.open("GET", _url + "index.json", false);
        req.send(null);
        var json_index = JSON.parse(req.responseText)
        var fs_index = {}
        var walk_index = function (path, dir) {
            logger(path, "walk_index")
            fs_index[path] = null
            if (path != "/") {
                path = path + "/"
            }
            for (var key in dir) {
                if (typeof dir[key] === 'object') {
                    walk_index(path + key, dir[key]) // toLowerCase to simulate a case-insensitive filesystem
                } else {
                    if (key !== "index.json") {
                        fs_index[path + key] = dir[key] // toLowerCase to simulate a case-insensitive filesystem
                    }
                }

            }
        }

        walk_index("/", json_index)

        let CUSTOM_FS = {
            url: _url,
            listDirectory: function (_path) {
                const path = _path.path
                var result = []
                for (var node in fs_index) {
                    if (node.startsWith(path) && node.lastIndexOf("/") <= path.length && node !== path && node.substr(path.length + 1).length > 0) {
                        result.push(node.substr(path.length + 1))
                    }
                }
                return { ok: true, data: result };
            },

            // used for open
            get: function (_path) {
                const path = _path.path
                logger(path, "get")
                if (path in fs_index) {
                    // if  fs_index[path] is still a integer (hence a file), we now initialize the array to store any file data
                    if (Number.isInteger(fs_index[path])) {
                        fs_index[path] = new Uint8Array(fs_index[path])
                    }
                    return { ok: true, data: fs_index[path] };
                } else {
                    return { ok: false }
                }
            },

            // used for close, mknod
            put: function (_path, data) {
                const path = _path.path
                logger(path, "put")
                /* we actually don't close files, it's a waste and triggers a lot of redownloads 
                    if (!data && typeof fs_index[path] == "object") {
                        fs_index[path] = fs_index[path].length // if data is undefined the file is closed and the value should be reset to the size (not null/undefined)
                    } else if (data) {
                        fs_index[path] = data
                    }
                */
                return { ok: true, data: fs_index[path] };
            },

            read: function (args) {
                const path = args.path;
                logger(path, "read, args:" + JSON.stringify(args))

                if (typeof fs_index[path] !== "object") {
                    console.error("File hasn't been opened yet")
                    throw new FS.ErrnoError(ERRNO_CODES.EPERM);
                }
                const start = args.start;
                const end = (args.end > (fs_index[path].length)) ? (fs_index[path].length) : args.end // sometimes we get requests beyond the end of the file (????)
                if (start > end) {
                    return { ok: true, data: [] };
                }
                var alreadyLoaded = false;
                for (var idx = 0; idx < end && idx < 1000; idx++) { // avoid checking whole file but check until end of read or at least first 1000 bytes
                    // TODO: This would break for all-0 files which would be redownloaded on each read
                    if (fs_index[path][idx] != 0) {
                        logger(path, "read: Found non-0 entry at " + idx + ", file is already cached")
                        alreadyLoaded = true
                        break;

                    }
                }

                let data = null;
                if (alreadyLoaded) {
                    data = new Uint8Array(end - start + 1);
                    for (var idx = start; idx <= end; idx++) {
                        data[idx - start] = fs_index[path][idx]
                    }
                } else {
                    const req = new XMLHttpRequest();
                    const url = _url + path;
                    req.open('GET', url, false);
                    // TODO: make this async and wait until indexOf(null,start) == -1 or indexOf(null,start) > length in cache
                    // On most platforms, we cannot set the responseType of synchronous downloads.
                    // @todo Test for this; IE10 allows this, as do older versions of Chrome/FF.

                    let err = null;
                    // Classic hack to download binary data as a string.
                    req.overrideMimeType('text/plain; charset=x-user-defined');

                    // Trying to use range requests where possible
                    // TODO: this is disabled as we can't yet properly cache range request results.
                    //       to do so would require changing the fileData array into an array of chunks (presumably 2MB or so) 
                    //       which can be updated and read invididually 
                    //req.setRequestHeader('Range', 'bytes=' + start + '-' + (fs_index[path].length - 1)); // the bytes (in

                    req.onreadystatechange = function (e) {
                        if (req.readyState === 4) {
                            if (req.status === 200 || req.status === 206) {

                                // Convert the text into a buffer.
                                var text = req.responseText;
                                if (text.length > end - start) { // range request wasn't respected. We assume this is the full answer
                                    var fullData = new Uint8Array(text.length);
                                    data = new Uint8Array(end - start + 1);
                                    // Throw away the upper bits of each character.
                                    logger(path, "Downloading " + text.length + " bytes");
                                    for (let i = 0; i < text.length; i++) {
                                        // This will automatically throw away the upper bit of each
                                        // character for us.
                                        if (i >= start && i <= end) {
                                            data[i - start] = text.charCodeAt(i);
                                        }
                                        fullData[i] = text.charCodeAt(i)
                                        // we don't yet cache, but this is the code: 
                                    }
                                    fs_index[path] = fullData
                                    logger(path, "Downloaded [full download]");
                                } else {
                                    data = new Uint8Array(end - start + 1);
                                    // Throw away the upper bits of each character.
                                    console.log("Reading " + text.length + "bytes for" + path);
                                    for (let i = 0; i < text.length; i++) {
                                        // This will automatically throw away the upper bit of each
                                        // character for us.

                                        if (i <= end - start) {

                                            data[i] = text.charCodeAt(i);
                                        }
                                        // we don't yet cache range requests: 
                                        // fs_index[path][start + i] = data[i]
                                    }
                                    logger(path, "Downloaded [range request]");
                                }
                            } else {
                                console.error(req);
                                throw new FS.ErrnoError(ERRNO_CODES.EINVAL);
                            }
                        }
                    };
                    req.send();
                    if (err) {
                        throw err;
                    }
                }
                return { ok: true, data: data };
            }
        }

        this.CUSTOM_FS = CUSTOM_FS;
        this.node_ops.getattr = (node) => {
            return {
                dev: 1,
                ino: node.id,
                mode: node.mode,
                nlink: 1,
                uid: 0,
                gid: 0,
                rdev: undefined,
                size: node.size,
                atime: new Date(node.timestamp),
                mtime: new Date(node.timestamp),
                ctime: new Date(node.timestamp),
                blksize: 4096,
                blocks: 0,
            };
        };

        this.node_ops.setattr = (node, attr) => {
            // Doesn't really do anything
            if (attr.mode !== undefined) {
                node.mode = attr.mode;
            }
            if (attr.timestamp !== undefined) {
                node.timestamp = attr.timestamp;
            }
        };

        this.node_ops.lookup = (parent, name) => {
            logger(name, "lookup ")
            if (parent instanceof FS.FSStream) { //sometimes we get a stream instead of a node
                parent = parent.node;
            }
            const path = realPath(parent, name);
            const result = this.CUSTOM_FS.get({ path });
            if (!result.ok) {
                // I wish Javascript had inner exceptions
                throw new FS.ErrnoError(ERRNO_CODES.ENOENT);
            }
            return this.createNode(parent, name, result.data === null ? DIR_MODE : FILE_MODE, result.data ? result.data.length : null);
        };

        this.node_ops.mknod = (parent, name, mode, dev) => {
            logger(name, "mknod ")
            const node = this.createNode(parent, name, mode, 0);
            const path = realPath(node);
            if (this.FS.isDir(node.mode)) {
                this.convertSyncResult(this.CUSTOM_FS.put({ path, value: null }));
            }
            else {
                this.convertSyncResult(this.CUSTOM_FS.put({ path, value: "" }));
            }
            return node;
        };

        this.node_ops.rename = (oldNode, newDir, newName) => {
            throw new FS.ErrnoError(ERRNO_CODES.EPERM);
            const oldPath = realPath(oldNode);
            const newPath = realPath(newDir, newName);
            this.convertSyncResult(this.CUSTOM_FS.move({ path: oldPath, newPath: newPath }));
            oldNode.name = newName;
        };

        this.node_ops.unlink = (parent, name) => {
            throw new FS.ErrnoError(ERRNO_CODES.EPERM);
            const path = realPath(parent, name);
            this.convertSyncResult(this.CUSTOM_FS.delete({ path }));
        };

        this.node_ops.rmdir = (parent, name) => {
            throw new FS.ErrnoError(ERRNO_CODES.EPERM);
            const path = realPath(parent, name);
            this.convertSyncResult(this.CUSTOM_FS.delete({ path }));
        };

        this.node_ops.readdir = (node) => {
            const path = realPath(node);
            let result = this.convertSyncResult(this.CUSTOM_FS.listDirectory({ path }));
            if (!result.includes(".")) {
                result.push(".");
            }
            if (!result.includes("..")) {
                result.push("..");
            }
            return result;
        };

        this.node_ops.symlink = (parent, newName, oldPath) => {
            throw new FS.ErrnoError(ERRNO_CODES.EPERM);
        };

        this.node_ops.readlink = (node) => {
            throw new FS.ErrnoError(ERRNO_CODES.EPERM);
        };

        this.stream_ops.open = (stream) => { // TODO: This actually shoudl also give a flag (w, r, r+ etc.). Which means we can enfore read only opens
            logger(stream.path, "Open stream ")
            const path = realPath(stream.node);
            if (FS.isFile(stream.node.mode)) {
                const result = this.convertSyncResult(this.CUSTOM_FS.get({ path }));
                if (result === null || result === undefined) {
                    return;
                }
                stream.fileData = result;
            }
        };

        this.stream_ops.close = (stream) => {
            logger(stream.path, "close stream ")
            const path = realPath(stream.node);
            if (FS.isFile(stream.node.mode) && stream.fileData) {
                const fileData = stream.fileData
                // TODO: Track open/closed files differently so we can warn but don't lose the cached data
                //stream.fileData = undefined;
                this.convertSyncResult(this.CUSTOM_FS.put({ path, value: fileData }));
            }
        };

        this.stream_ops.read = (stream, buffer, offset, length, position) => {
            if (!position) {
                position = stream.position
            }
            logger(stream.path, "read stream - offset:" + offset + " length:" + length + " position:" + position)
            const path = realPath(stream.node);
            var _a, _b;
            if (length <= 0)
                return 0;

            var size = length
            if (typeof stream.fileData === 'object' && stream.fileData.length < position + length) {
                size = stream.fileData.length - position
            }

            logger(stream.path, "Length, Position " + length + "," + position)
            logger(stream.path, "Size " + size)
            logger(stream.path, "stream.fileData.length " + stream.fileData.length)
            if (size < 0) {
                throw new FS.ErrnoError(ERRNO_CODES.EINVAL);
            }
            if (size > 0) {
                var fileData = this.convertSyncResult(this.CUSTOM_FS.read({ path: path, start: position, end: position + size - 1 }));
                logger(stream.path, "fileData (start: " + (position) + " end: " + (position + size - 1).toString() + " (length: " + fileData.length + ")")
                function Uint8Array2hex(byteArray) {
                    return Array.prototype.map.call(byteArray, function (byte) {
                        return ('0' + (byte & 0xFF).toString(16)).slice(-2).toUpperCase();
                    }).join(' ');
                }
                logger(stream.path, Uint8Array2hex(fileData))
                buffer.set(fileData, offset);
            }
            //    buffer.set(stream.fileData.subarray(position, position + size), offset);

            return size;
        };

        this.stream_ops.write = (stream, buffer, offset, length, position) => {
            var _a, _b, _c;
            if (length <= 0)
                return 0;
            stream.node.timestamp = Date.now();
            try {
                if (position + length > ((_b = (_a = stream.fileData) === null || _a === void 0 ? void 0 : _a.length) !== null && _b !== void 0 ? _b : 0)) {
                    // Resize
                    const oldData = (_c = stream.fileData) !== null && _c !== void 0 ? _c : new Uint8Array();
                    stream.fileData = new Uint8Array(position + length);
                    stream.fileData.set(oldData);
                }
                // Write
                stream.fileData.set(buffer.subarray(offset, offset + length), position);
                return length;
            }
            catch (e) {
                console.error(e)
                throw new FS.ErrnoError(ERRNO_CODES.EPERM);
            }
        };

        this.stream_ops.llseek = (stream, offset, whence) => {
            let position = offset; // SEEK_SET
            if (whence === SEEK_CUR) {
                position += stream.position;
            }
            else if (whence === SEEK_END) {
                if (this.FS.isFile(stream.node.mode)) {
                    position += stream.fileData.length;
                }
            } else if (whence !== SEEK_SET) {
                console.error("Illegal Whence: " + whence)
                throw new FS.ErrnoError(ERRNO_CODES.EINVAL);
            }
            if (position < 0) {
                console.error("CRITICAL: Position < 0")
                throw new FS.ErrnoError(ERRNO_CODES.EINVAL);
            }
            stream.position = position
            return position;
        };
    }

    mount(mount) {
        return this.createNode(null, "/", DIR_MODE, 0);
    }

    createNode(parent, name, mode, size) {
        logger(name, "createNode")
        if (!this.FS.isDir(mode) && !this.FS.isFile(mode)) {
            throw new FS.ErrnoError(ERRNO_CODES.EINVAL);
        }
        let node = this.FS.createNode(parent, name, mode);
        node.node_ops = this.node_ops;
        node.stream_ops = this.stream_ops;
        node.size = size
        return node;
    }

    convertSyncResult(result) {
        if (result.ok) {
            return result.data;
        }
        else {
            let error;
            if (result.status === 404) {
                error = new FS.ErrnoError(ERRNO_CODES.ENOENT);
            }
            else {
                error = new FS.ErrnoError(ERRNO_CODES.EPERM);
            }
            // I'm so looking forward to https://github.com/tc39/proposal-error-cause
            error.cause = result.error;
            throw error;
        }
    }
}

function realPath(node, fileName) {
    const parts = [];
    while (node.parent !== node) {
        parts.push(node.name);
        node = node.parent;
    }
    parts.push(node.mount.opts.root);
    parts.reverse();
    if (fileName !== undefined && fileName !== null) {
        parts.push(fileName);
    }
    return parts.join("/");
}

// Helper Function to compare lazy loaded data vs. embedded data, eg. with the following command
// ScummvmFS.testFilesystem("/ft-dos-demo-en/VIDEO/","/games/ft-dos-demo-en/VIDEO/")
ScummvmFS.testFilesystem = function (path1, path2) {
    for (var file of FS.readdir(path1).sort()) {
        if (!file.startsWith(".")) {
            const stat = FS.stat(path1 + file)
            if (FS.isFile(stat.mode)) {
                const file1 = FS.readFile(path1 + file)
                const file2 = FS.readFile(path2 + file)
                if (file1.length != file2.length) { throw new Error("Size Mismatch") } else {
                    console.error(file + ": Size matches")
                }
                for (var i = 0; i < file1.length; i++) {
                    if (file1[i] != file2[i]) {
                        throw new Error("Data mismatch");
                    }
                }
                console.error(file + ": data matches")
                var stream1 = FS.open(path1 + file, "r")
                var stream2 = FS.open(path2 + file, "r")
                FS.llseek(stream1, 100, 1)
                FS.llseek(stream2, 100, 1)
                var buf1 = new Uint8Array(100);
                var buf2 = new Uint8Array(100);
                FS.read(stream1, buf1, 0, 100);
                FS.read(stream2, buf2, 0, 100);
                FS.closeStream(stream1)
                FS.closeStream(stream2)
                for (var i = 0; i < buf1.length; i++) {
                    if (buf1[i] != buf2[i]) {
                        console.log(buf1)
                        console.log(buf2)
                        throw new Error("Data mismatch")
                    }
                }
                console.error(file + ": data matches")
            }
        }
    }

}