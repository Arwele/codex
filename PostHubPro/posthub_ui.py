import adsk.core
import traceback
import os
from datetime import datetime

from . import file_manager, tag_manager, versioning, export_import, sync_manager

handlers = []


class CommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def notify(self, args: adsk.core.CommandCreatedEventArgs):
        ui = adsk.core.Application.get().userInterface
        try:
            cmd = args.command
            inputs = cmd.commandInputs
            self.table = inputs.addTableCommandInput('fileTable', 'Post Files', 4, '1:1:1:1')
            self.table.maximumVisibleRows = 10
            files = file_manager.list_cps_files()
            for i, meta in enumerate(files):
                row = self.table.rowCount
                name_in = inputs.addStringValueInput(f'name_{i}', '', meta['name'])
                mod = datetime.fromtimestamp(meta['modified']).strftime('%Y-%m-%d %H:%M')
                mod_in = inputs.addStringValueInput(f'mod_{i}', '', mod)
                tags = ', '.join(tag_manager.get_tags_for_file(meta['path']))
                tag_in = inputs.addStringValueInput(f'tag_{i}', '', tags)
                status = sync_manager.file_status(meta['path'])
                status_in = inputs.addStringValueInput(f'status_{i}', '', status)
                self.table.addCommandInput(name_in, row, 0)
                self.table.addCommandInput(mod_in, row, 1)
                self.table.addCommandInput(tag_in, row, 2)
                self.table.addCommandInput(status_in, row, 3)

            inputs.addSeparatorCommandInput('sep1')
            inputs.addBoolValueInput('backupNow', 'Backup Now', False, '', False)
            inputs.addBoolValueInput('syncNow', 'Sync Now', False, '', False)
            inputs.addBoolValueInput('setSync', 'Set Sync Folder', False, '', False)
            inputs.addBoolValueInput('restoreLatest', 'Restore Latest', False, '', False)
            inputs.addBoolValueInput('saveTags', 'Save Tags', False, '', False)
            inputs.addBoolValueInput('exportZip', 'Export ZIP', False, '', False)
            inputs.addBoolValueInput('importZip', 'Import ZIP', False, '', False)
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def notify(self, args: adsk.core.CommandEventArgs):
        ui = adsk.core.Application.get().userInterface
        try:
            inputs = args.command.commandInputs
            if inputs.itemById('backupNow').value:
                for f in file_manager.list_cps_files():
                    versioning.backup_file(f['path'])
                ui.messageBox('Backup complete')
            if inputs.itemById('syncNow').value:
                files = [f['path'] for f in file_manager.list_cps_files()]
                res = sync_manager.sync_all(files)
                msg = '\n'.join([f"{os.path.basename(k)}: {v}" for k, v in res.items()])
                ui.messageBox('Sync complete:\n' + msg)
            if inputs.itemById('setSync').value:
                dlg = ui.createFolderDialog()
                dlg.title = 'Select Sync Folder'
                if dlg.showDialog() == adsk.core.DialogResults.DialogOK:
                    sync_manager.set_sync_folder(dlg.folder)
                    ui.messageBox('Sync folder set')
            if inputs.itemById('restoreLatest').value:
                dlg = ui.createFileDialog()
                dlg.filter = 'CPS (*.cps)'
                if dlg.showOpen() == adsk.core.DialogResults.DialogOK:
                    if versioning.restore_latest(dlg.filename):
                        ui.messageBox('File restored')
                    else:
                        ui.messageBox('No backup found')
            if inputs.itemById('saveTags').value:
                files = file_manager.list_cps_files()
                for i, meta in enumerate(files):
                    inp = inputs.itemById(f'tag_{i}')
                    if inp:
                        tags = [t.strip() for t in inp.value.split(',') if t.strip()]
                        tag_manager.update_tags_for_file(meta['path'], tags)
                ui.messageBox('Tags saved')
            if inputs.itemById('exportZip').value:
                dlg = ui.createFileDialog()
                dlg.isMultiSelectEnabled = False
                dlg.filter = 'Zip (*.zip)'
                if dlg.showSave() == adsk.core.DialogResults.DialogOK:
                    paths = [f['path'] for f in file_manager.list_cps_files()]
                    export_import.export_zip(paths, dlg.filename)
                    ui.messageBox('ZIP exported')
            if inputs.itemById('importZip').value:
                dlg = ui.createFileDialog()
                dlg.isMultiSelectEnabled = False
                dlg.filter = 'Zip (*.zip)'
                if dlg.showOpen() == adsk.core.DialogResults.DialogOK:
                    export_import.import_zip(dlg.filename, file_manager.posts_folder())
                    ui.messageBox('ZIP imported')
        except:
            ui.messageBox('Error:\n{}'.format(traceback.format_exc()))


def show_dialog():
    app = adsk.core.Application.get()
    ui = app.userInterface
    cmd_def = ui.commandDefinitions.itemById('PostHubPro_cmd')
    if not cmd_def:
        cmd_def = ui.commandDefinitions.addButtonDefinition('PostHubPro_cmd', 'PostHub Pro', 'Manage post files')
    on_create = CommandCreatedHandler()
    on_execute = CommandExecuteHandler()
    cmd_def.commandCreated.add(on_create)
    cmd_def.execute()
    handlers.append(on_create)
    handlers.append(on_execute)
    app.log('PostHub Pro dialog shown')
