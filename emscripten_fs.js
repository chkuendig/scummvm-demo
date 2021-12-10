// based on https://github.com/gzuidhof/starboard-python/blob/867df3a341beed6ffc7c2ff8b80b1394982ce605/src/worker/emscripten-fs.ts
// see also
// https://github.com/jvilk/BrowserFS/blob/master/src/generic/emscripten_fs.ts
// https://github.com/emscripten-core/emscripten/blob/main/src/library_nodefs.js
// https://github.com/emscripten-core/emscripten/blob/main/src/library_memfs.js
// https://github.com/emscripten-core/emscripten/blob/main/src/library_workerfs.js
// https://github.com/curiousdannii/emglken/blob/master/src/emglkenfs.js
const DIR_MODE = 16895; // 040777
const FILE_MODE = 33206; // 100666
const SEEK_CUR = 1;
const SEEK_END = 2;
const encoder = new TextEncoder();
const decoder = new TextDecoder("utf-8");
function _split_path(p) {
    const dirpath = p.substr(0, p.lastIndexOf("/"));
    const itemname = p.substr(dirpath.length + (dirpath === "/" ? 0 : 1));
    return [dirpath, itemname];
}
export class EMFS {
    constructor(FS, ERRNO_CODES, _url) {
        this.node_ops = {};
        this.stream_ops = {};
        this.FS = FS;
        this.ERRNO_CODES = ERRNO_CODES;

        var req = new XMLHttpRequest(); // a new request
        req.open("GET", _url + "index.new.json", false);
        req.send(null);
        var json_index = JSON.parse(req.responseText)
        var fs_index = {}
        var walk_index = function (path, dir) {
            fs_index[path] = null
            if (path != "/") {
                path = path + "/"
            }
            for (var key in dir) {
                if (typeof dir[key] === 'object') {
                    walk_index(path + key, dir[key])
                } else {
                    fs_index[path + key] = dir[key]
                }

            }
        }
        walk_index("/", json_index)
        console.log(fs_index)
        let CUSTOM_FS = {
            url: _url,
            listDirectory: function (_path) {
                const path = _path.path
                var result = []
                for (var node in fs_index) {
                    if (node.startsWith(path) && node.lastIndexOf("/") <= path.length && node !== path) {
                        result.push(node.substr(path.length + 1))
                    }
                }
                return { ok: true, data: result };
            },
            // used for open
            get: function (_path) {
                const path = _path.path
                if (path in fs_index) {
                    // if  fs_index[path] is still a integer, we now initialize the array to store any file data
                    if (Number.isInteger(fs_index[path])) {
                        fs_index[path] = new Uint8Array(fs_index[path])
                    }
                    return { ok: true, data: fs_index[path] };
                } else {
                    return { ok: false }
                }
            },
            // used for close, mknod
            put: function (path, data) {

                fs_index[path] = data
                return { ok: true, data: fs_index[path] };
            },
            read: function (args) {
                const path = args.path;
                const start = args.start;
                const end = args.end
                if (typeof fs_index[path] !== "object") {
                    console.log(typeof fs_index[path])
                    console.log(fs_index[path])
                    throw new Error("File hasn't been opened yet)")
                }

                var alreadyLoaded = true;
                for (var idx = start; idx <= end; idx++) {
                    if (!fs_index[path][idx]) {
                        if(alreadyLoaded){
                            console.log("Missing idx "+idx)
                        }
                        alreadyLoaded = false
                    }
                }
                let data = null;
                if (alreadyLoaded) {
                    console.log("data cached...") 
                    data = new Uint8Array(args.end - args.start + 1);
                    for (var idx = start; idx <= end; idx++) {
                        data = fs_index[path][idx]
                    }
                }

                else {


                    const req = new XMLHttpRequest();
                    const url = _url + path;
                    console.log(url)
                    req.open('GET', url, false);
                    // TODO: make this async and wait until indexOf(null,start) == -1 or indexOf(null,start) > length in cache

                    // On most platforms, we cannot set the responseType of synchronous downloads.
                    // @todo Test for this; IE10 allows this, as do older versions of Chrome/FF.

                    let err = null;
                    // Classic hack to download binary data as a string.
                    req.overrideMimeType('text/plain; charset=x-user-defined');
                    req.setRequestHeader('Range', 'bytes=' + args.start + '-' + fs_index[path].length); // the bytes (in
                    // 
                    // need to keep hold of start?
                    /* 
                    https://nodejs.org/api/fs.html#fs_filehandle_read_buffer_offset_length_position
                    Reads data from the file and stores that in the given buffer.
    
    If the file is not modified concurrently, the end-of-file is reached when the number of bytes read is zero.
    */

                    req.onreadystatechange = function (e) {
                        if (req.readyState === 4) {
                            if (req.status === 200 || req.status === 206) {

                                // Convert the text into a buffer.
                                const text = req.responseText;
                                data = new Uint8Array(end-start+1);
                                // Throw away the upper bits of each character.
                                for (let i = 0; i < text.length; i++) {
                                    // This will automatically throw away the upper bit of each
                                    // character for us.
                                    fs_index[path][start+i] = data[i]
                                    if(i<=end-start) {

                                        data[i] = text.charCodeAt(i);
                                    }
                                }


                            } else {
                                console.log(req);
                                throw new FS.ErrnoError(ERRNO_CODES["EINVAL"]);

                            }
                        }
                    };
                    req.send();
                    if (err) {
                        throw err;
                    }
                    if (data.length < 100) {
                        console.log(data)
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
                size: 0,
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
            if (parent instanceof FS.FSStream) { //sometimes we get a stream instead of a node
                parent = parent.node;
            }
            const path = realPath(parent, name);
            const result = this.CUSTOM_FS.get({ path });
            if (!result.ok) {
                // I wish Javascript had inner exceptions
                throw this.FS.genericErrors[this.ERRNO_CODES["ENOENT"]];
            }
            return this.createNode(parent, name, result.data === null ? DIR_MODE : FILE_MODE);
        };
        this.node_ops.mknod = (parent, name, mode, dev) => {
            const node = this.createNode(parent, name, mode, dev);
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
            const oldPath = realPath(oldNode);
            const newPath = realPath(newDir, newName);
            this.convertSyncResult(this.CUSTOM_FS.move({ path: oldPath, newPath: newPath }));
            oldNode.name = newName;
        };
        this.node_ops.unlink = (parent, name) => {
            const path = realPath(parent, name);
            this.convertSyncResult(this.CUSTOM_FS.delete({ path }));
        };
        this.node_ops.rmdir = (parent, name) => {
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
            throw new FS.ErrnoError(this.ERRNO_CODES["EPERM"]);
        };
        this.node_ops.readlink = (node) => {
            throw new FS.ErrnoError(this.ERRNO_CODES["EPERM"]);
        };
        this.stream_ops.open = (stream) => {
            const path = realPath(stream.node);
            if (FS.isFile(stream.node.mode)) {
                const result = this.convertSyncResult(this.CUSTOM_FS.get({ path }));
                if (result === null) {
                    return;
                }
                stream.fileData = result;
            }
        };
        this.stream_ops.close = (stream) => {
            const path = realPath(stream.node);
            if (FS.isFile(stream.node.mode) && stream.fileData) {
                const fileData = stream.fileData
                stream.fileData = undefined;
                this.convertSyncResult(this.CUSTOM_FS.put({ path, value: fileData }));
            }
        };
        this.stream_ops.read = (stream, buffer, offset, length, position) => {

            const path = realPath(stream.node);
            var _a, _b;
            if (length <= 0)
                return 0;
            const size = Math.min(((_b = (_a = stream.fileData) === null || _a === void 0 ? void 0 : _a.length) !== null && _b !== void 0 ? _b : 0) - position + 1, length);
            console.log("Length, Position", length, position)
            console.log("Size", size)
            if (size <= 0) {
                throw new FS.ErrnoError(this.ERRNO_CODES["EPERM"]);
            }
            try {

                var fileData = this.convertSyncResult(this.CUSTOM_FS.read({ path: path, start: position, end: position + size - 1 }));

                //  if(fileData.length < 100) {
                console.log("fileData")
                console.log(fileData)
                //        }
                buffer.set(fileData, offset);
                //    buffer.set(stream.fileData.subarray(position, position + size), offset);
            }
            catch (e) {
                throw new FS.ErrnoError(this.ERRNO_CODES["EPERM"]);
            }
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
                throw new FS.ErrnoError(this.ERRNO_CODES["EPERM"]);
            }
        };
        this.stream_ops.llseek = (stream, offset, whence) => {
            let position = offset;
            if (whence === SEEK_CUR) {
                position += stream.position;
            }
            else if (whence === SEEK_END) {
                if (this.FS.isFile(stream.node.mode)) {
                    try {
                        // Not sure, but let's see
                        position += stream.fileData.length;
                    }
                    catch (e) {
                        throw new FS.ErrnoError(this.ERRNO_CODES["EPERM"]);
                    }
                }
            }
            if (position < 0) {
                throw new FS.ErrnoError(this.ERRNO_CODES["EINVAL"]);
            }
            return position;
        };
    }
    mount(mount) {
        return this.createNode(null, "/", DIR_MODE, 0);
    }
    createNode(parent, name, mode, dev) {
        if (!this.FS.isDir(mode) && !this.FS.isFile(mode)) {
            throw new this.FS.ErrnoError(this.ERRNO_CODES["EINVAL"]);
        }
        let node = this.FS.createNode(parent, name, mode);
        node.node_ops = this.node_ops;
        node.stream_ops = this.stream_ops;
        return node;
    }
    convertSyncResult(result) {
        if (result.ok) {
            return result.data;
        }
        else {
            let error;
            if (result.status === 404) {
                error = new this.FS.ErrnoError(this.ERRNO_CODES["ENOENT"]);
            }
            else {
                error = new this.FS.ErrnoError(this.ERRNO_CODES["EPERM"]);
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
