import { loadPyodide } from "https://cdn.jsdelivr.net/pyodide/v0.23.4/full/pyodide.mjs";

const consoleEl = document.getElementById("console");
function write(text) {
  consoleEl.textContent += text + "\n";
  consoleEl.scrollTop = consoleEl.scrollHeight;
}

async function loadGame(pyodide) {
  const files = [
    "battle.py",
    "characters.py",
    "dialogues.py",
    "equipment.py",
    "game.py",
    "gui.py",
    "items.py",
    "locations.py",
    "messages.py",
    "utils.py",
    "data/actions.json",
    "data/characters.json",
    "data/dialogues.json",
    "data/groups.json",
    "data/items.json",
    "data/keywords.json",
    "data/locations.json",
    "data/messages.json",
    "data/quests.json",
  ];
  for (const file of files) {
    const resp = await fetch(file);
    const data = await resp.text();
    const path = file;
    const dir = path.substring(0, path.lastIndexOf("/"));
    if (dir) {
      pyodide.FS.mkdirTree(dir);
    }
    pyodide.FS.writeFile(path, data);
  }
}

async function main() {
  const pyodide = await loadPyodide({ indexURL: "https://cdn.jsdelivr.net/pyodide/v0.23.4/full/" });
  pyodide.setStdout({ batched: (s) => write(s) });
  pyodide.setStderr({ batched: (s) => write(s) });
  await loadGame(pyodide);
  await pyodide.runPythonAsync(`import game\nmain()`);
}

document.getElementById("start").addEventListener("click", () => {
  document.getElementById("start").disabled = true;
  main();
});
