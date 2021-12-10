/*

Emglken File System
===================

Copyright (c) 2020 Dannii Willis
MIT licenced
https://github.com/curiousdannii/emglken

*/

const DIR_MODE = 16895 // 040777
const FILE_MODE = 33206 // 100666
const SEEK_SET = 0
const SEEK_CUR = 1
const SEEK_END = 2

// WASI error codes
// See https://github.com/WebAssembly/wasi-libc/blob/master/libc-bottom-half/headers/public/wasi/api.h
const EINVAL = 28
const ENOENT = 44

// Convert Linux flags to Glk flags
const filemode_Write = 1
const filemode_Read = 2
const filemode_ReadWrite = 3
const filemode_WriteAppend = 5
function convert_flags(flags)
{
    // O_APPEND => filemode_WriteAppend
    if (flags & 0x400)
    {
        return filemode_WriteAppend
    }
    // O_WRONLY => filemode_Write
    if (flags & 1)
    {
        return filemode_Write
    }
    // O_RDWR => filemode_ReadWrite
    if (flags & 2)
    {
        return filemode_ReadWrite
    }
    // O_RDONLY => filemode_Read
    return filemode_Read
}

// Functions for storing Uint8Arrays in localStorage
function String_to_Uint8Array(str)
{
    return Uint8Array.from(str, ch => ch.charCodeAt(0))
}

function Uint8Array_to_String(array)
{
    return array.reduce((prev, ch) => prev + String.fromCharCode(ch), '')
}

module.exports = class EmglkenFS
{
    constructor(VM)
    {
        this.dialog = VM.options.Dialog
        this.streaming = this.dialog.streaming
        this.FS = VM.Module.FS
        this.VM = VM

        this.filename_map = {}
        this.filename_counter = 0
    }

    close(stream)
    {
        if (stream.name === 'storyfile')
        {}
        else
        {
            if (this.streaming)
            {
                stream.fstream.fclose()
            }
            else
            {
                if (stream.fmode !== filemode_Read)
                {
                    this.dialog.file_write(stream.fref, Uint8Array_to_String(stream.data), true)
                }
            }
        }
    }

    createNode(parent, name, mode/*, dev*/)
    {
        const FS = this.FS
        if (!FS.isDir(mode) && !FS.isFile(mode))
        {
            throw new FS.ErrnoError(EINVAL)
        }
        const node = FS.createNode(parent, name, mode)
        node.node_ops = this
        node.stream_ops = this
        node.timestamp = Date.now()
        return node
    }

    getattr(node)
    {
        // At present only the size of the storyfile will be returned, as needed by Bocfel
        const size = node.name === 'storyfile' ? this.VM.data.length : 0

        // Not sure what to return here, so only return stuff some of it
        return {
            atime: new Date(node.timestamp),
            ctime: new Date(node.timestamp),
            dev: 1,
            gid: 0,
            ino: node.id,
            mode: node.mode,
            mtime: new Date(node.timestamp),
            nlink: 1,
            rdev: node.rdev,
            size,
            uid: 0,
        }
    }

    // Get a Dialog ref for non-streaming Dialogs
    get_dialog_ref(filename)
    {
        let [name, usage] = filename.split('.')

        // RemGlk sends usages starting with 'glk', but Dialog wants them without
        usage = usage.replace('glk', '')

        // Retrieve the game ID if opening a savefile
        let gameid = ''
        if (usage === 'save')
        {
            gameid = this.VM.Module.AsciiToString(this.VM.Module._gidispatch_get_game_id())
        }

        return this.dialog.file_construct_ref(name, usage, gameid)
    }

    llseek(stream, offset, whence)
    {
        let position = offset
        if (whence === SEEK_CUR)
        {
            position += stream.position
        }
        else if (whence === SEEK_END)
        {
            if (stream.name === 'storyfile')
            {
                position += stream.data.length
            }
            else
            {
                if (this.streaming)
                {
                    const curpos = stream.fstream.ftell()
                    stream.fstream.fseek(0, SEEK_END)
                    position += stream.fstream.ftell()
                    stream.fstream.fseek(curpos, SEEK_SET)
                }
                else
                {
                    position += stream.data.length
                }
            }
        }
        if (position < 0)
        {
            throw new this.FS.ErrnoError(EINVAL)
        }
        return position
    }

    lookup(parent, name)
    {
        if (name !== 'storyfile')
        {
            const realname = this.filename_map[name] || name
            if (!this.dialog.file_ref_exists(this.streaming ? {filename: realname} : this.get_dialog_ref(realname)))
            {
                throw new this.FS.ErrnoError(ENOENT)
            }
        }
        return this.createNode(parent, name, FILE_MODE)
    }

    mknod(parent, name, mode/*, dev*/)
    {
        return this.createNode(parent, name, mode)
    }

    mmap()
    {
        throw new Error('EmglkenFS.mmap')
    }

    mount()
    {
        return this.createNode(null, '/', DIR_MODE, 0)
    }

    msync()
    {
        throw new Error('EmglkenFS.msync')
    }

    open(stream)
    {
        stream.name = stream.node.name
        if (stream.name === 'storyfile')
        {
            stream.data = this.VM.data
        }
        else
        {
            const fmode = convert_flags(stream.flags)
            const realname = this.filename_map[stream.name] || stream.name
            if (this.streaming)
            {
                stream.fstream = this.dialog.file_fopen(fmode, {filename: realname})
            }
            else
            {
                stream.fref = this.get_dialog_ref(realname)
                stream.fmode = fmode

                // Read the content if not overwriting
                let data = null
                if (fmode !== filemode_Write)
                {
                    data = this.dialog.file_read(stream.fref, true)
                }

                // If no file and not reading, create a blank file
                if (data == null)
                {
                    stream.data = new Uint8Array(0)
                    if (fmode !== filemode_Read)
                    {
                        this.dialog.file_write(stream.fref, '', true)
                    }
                }
                else
                {
                    stream.data = String_to_Uint8Array(data)
                }
                //stream.position = fmode === filemode_WriteAppend ? data.length : 0
            }
        }
    }

    read(stream, buffer, offset, length, position)
    {
        if (length === 0)
        {
            return 0
        }
        if (stream.name === 'storyfile')
        {
            const size = Math.min(stream.data.length - position, length)
            buffer.set(stream.data.subarray(position, position + size), offset)
            return size
        }
        else
        {
            if (this.streaming)
            {
                stream.fstream.fseek(position, SEEK_SET)
                const buf = stream.fstream.BufferClass.from(buffer.buffer, offset, length)
                return stream.fstream.fread(buf, length)
            }
            else
            {
                const size = Math.min(stream.data.length - position, length)
                buffer.set(stream.data.subarray(position, position + size), offset)
                return size
            }
        }
    }

    readdir()
    {
        throw new Error('EmglkenFS.readdir')
    }

    readlink()
    {
        throw new Error('EmglkenFS.readlink')
    }

    // electrofs.js will give a full system path, which we can't handle. So store the full path and return a fake file name
    register_filename(filename, usage)
    {
        const suffix = usage === 'save' ? '.glksave' : (usage === 'data' ? '.glkdata' : '.txt')
        if (!/\.(glkdata|glksave|txt)$/.test(filename))
        {
            filename = filename + suffix
        }

        if (this.filename_map[filename])
        {
            return this.filename_map[filename]
        }

        const fakename = 'emglken_fake_file_' + this.filename_counter++
        this.filename_map[filename] = fakename
        this.filename_map[fakename + suffix] = filename
        return fakename
    }

    rename()
    {
        throw new Error('EmglkenFS.rename')
    }

    rmdir()
    {
        throw new Error('EmglkenFS.rmdir')
    }

    setattr(/*node, attr*/)
    {
        // I don't think we need to do anything here?
        // Maybe truncate a file?
    }

    symlink()
    {
        throw new Error('EmglkenFS.symlink')
    }

    unlink(parent, name)
    {
        const realname = this.filename_map[name] || name
        this.dialog.file_remove_ref(this.get_dialog_ref(realname))
    }

    write(stream, buffer, offset, length, position)
    {
        if (stream.name === 'storyfile')
        {
            throw new Error('EmglkenFS.write: cannot write to storyfile')
        }
        if (this.streaming)
        {
            stream.fstream.fseek(position, SEEK_SET)
            const buf = stream.fstream.BufferClass.from(buffer).subarray(offset, offset + length)
            return stream.fstream.fwrite(buf, length)
        }
        else
        {
            position = position || stream.position
            const end_of_write = length + position
            if (end_of_write > stream.data.length)
            {
                const old_data = stream.data
                stream.data = new Uint8Array(end_of_write)
                stream.data.set(old_data)
            }
            stream.data.set(buffer.subarray(offset, offset + length), position)
            return length
        }
    }
}