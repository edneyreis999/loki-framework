# Plugin Activation And Namespace

Use this reference when creating, editing, or activating RPG Maker MZ plugins.

## Activation

A plugin file under `js/plugins/` is inert until the project loads it. In RPG Maker MZ, active plugin state and saved parameters are represented through the plugin manager data, commonly `js/plugins.js` in deployed projects.

Do not treat header `@param` defaults as proof of runtime configuration. Confirm the effective parameters in the active plugin list.

## Activation Review

Before editing `plugins.js`:

1. Confirm the task authorizes activation, not only file creation.
2. Preserve existing plugin order unless there is a reason to change it.
3. Preserve existing parameter values unless the task names a new value.
4. Explain any manual Plugin Manager step if file activation is unsafe.
5. Require Playtest when active behavior changes.

## Namespace Preservation

Project helper plugins often expose a global namespace. Preserve accumulated APIs instead of replacing the whole object.

Preferred pattern:

```js
(() => {
  "use strict";

  const root = globalThis.ProjectNamespace = globalThis.ProjectNamespace || {};

  Object.assign(root, {
    helperName() {
      // implementation
    }
  });
})();
```

Avoid:

```js
globalThis.ProjectNamespace = {
  helperName() {}
};
```

The second form can delete helpers added by another plugin or earlier patch.

## Validation

- Run `node -c` for edited plugin files.
- Confirm header tags required by the project.
- Confirm plugin commands and parameter names match the manager data.
- Confirm browser/Playtest behavior when touching `Scene_Map`, `Graphics`, `Input`, pictures, audio, save data or Common Event flow.
