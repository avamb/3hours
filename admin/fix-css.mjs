import fs from 'fs';
import { fileURLToPath } from 'url';

const cssPath = fileURLToPath(new URL('./static/styles.css', import.meta.url));
let css = fs.readFileSync(cssPath, 'utf8');

// Fix screen management
css = css.replace(
    '.screen {\n    display: none;\n}',
    '.screen {\n    display: none !important;\n}'
);

css = css.replace(
    '.screen.active {\n    display: block;\n}',
    '.screen.active {\n    display: block !important;\n}'
);

// Fix login screen
css = css.replace(
    '#login-screen {\n    min-height: 100vh;\n    display: flex;\n    align-items: center;\n    justify-content: center;',
    '#login-screen {\n    position: fixed;\n    top: 0;\n    left: 0;\n    right: 0;\n    bottom: 0;\n    min-height: 100vh;\n    align-items: center;\n    justify-content: center;\n    z-index: 1000;'
);

css = css.replace(
    '#login-screen.active {\n    display: flex;\n}',
    '#login-screen.active {\n    display: flex !important;\n}'
);

// Fix dashboard screen
css = css.replace(
    '#dashboard-screen {\n    display: grid;',
    '#dashboard-screen {\n    display: none;'
);

css = css.replace(
    '#dashboard-screen.active {\n    display: grid;\n}',
    '#dashboard-screen.active {\n    display: grid !important;\n}'
);

fs.writeFileSync(cssPath, css);
console.log('CSS fixed!');
