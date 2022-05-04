// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import * as cp from 'child_process';
import { executionAsyncId } from 'async_hooks';

async function exec(cmd: string) {
	const _exec = (cmd: string) =>
		new Promise<string>((resolve, reject) => {
			cp.exec(cmd, (err, out) => {
				if (err) {
					return reject(err);
				} else {
					return resolve(out);
				}
			});
		});

	return await _exec(cmd);
}

// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {
	
	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('Activating mandel-utils');
	exec('dune --start-container');

	// The command has been defined in the package.json file
	// Now provide the implementation of the command with registerCommand
	// The commandId parameter must match the command field in package.json
	let disposable = vscode.commands.registerCommand('mandel-utils.helloWorld', () => {
		// The code you place here will be executed every time your command is executed
		// Display a message box to the user
		vscode.window.showInformationMessage('Hello World from mandel-utils***!');
		vscode.window.showWarningMessage("OOPS");
		var cc = exec('dune --simple-list');
		cc.then((val) => val)
		   .then((val) => vscode.window.showInformationMessage(val))
			.catch((err) => vscode.window.showErrorMessage(err.message));
	});

	context.subscriptions.push(disposable);
}

// this method is called when your extension is deactivated
export function deactivate() {
	vscode.window.showInformationMessage('Stopping DUNE container');
	exec('dune --stop-container');
}
