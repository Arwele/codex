import adsk.core
import traceback

from . import posthub_ui

handlers = []
ui = None


class ShowDialogHandler(adsk.core.CommandCreatedEventHandler):
    def notify(self, args: adsk.core.CommandCreatedEventArgs):
        try:
            posthub_ui.show_dialog()
        except:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def run(context):
    global ui
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        cmd_def = ui.commandDefinitions.itemById('PostHubPro_Button')
        if not cmd_def:
            cmd_def = ui.commandDefinitions.addButtonDefinition('PostHubPro_Button', 'PostHub Pro', 'Manage post processors')
        on_cmd = ShowDialogHandler()
        cmd_def.commandCreated.add(on_cmd)
        handlers.append(on_cmd)
        workspace = ui.workspaces.itemById('CAMEnvironment')
        panel = workspace.toolbarPanels.itemById('CAMActionPanel')
        panel.controls.addCommand(cmd_def)
    except:
        if ui:
            ui.messageBox('Add-in start failed:\n{}'.format(traceback.format_exc()))


def stop(context):
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        workspace = ui.workspaces.itemById('CAMEnvironment')
        panel = workspace.toolbarPanels.itemById('CAMActionPanel')
        ctrl = panel.controls.itemById('PostHubPro_Button')
        if ctrl:
            ctrl.deleteMe()
        cmd = ui.commandDefinitions.itemById('PostHubPro_Button')
        if cmd:
            cmd.deleteMe()
    except:
        if ui:
            ui.messageBox('Add-in stop failed:\n{}'.format(traceback.format_exc()))
