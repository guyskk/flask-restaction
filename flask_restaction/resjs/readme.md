# res.js

用法

    npm install -g resjs

    resjs --help


    Usage: resjs [options] <url>

    generate res.js for browser or nodejs

    Options:

    -h, --help             output usage information
    -V, --version          output the version number
    -d, --dest [dest]      dest path to save res.js
    -p, --prefix [prefix]  url prefix of generated res.js
    -n, --node [node]      generate res.js for nodejs, default for browser
    -r, --rn [rn]          generate res.js for react-native
    -m, --min [min]        minimize generated res.js, default not minimize

ReactNative

    resjs APIURL -p APIURL --rn

构建

    cd resjs
    npm install
    npm run build

准备测试

    // create a server for test
    cd server
    pip install -r requires.txt
    python index.py

测试

    cd resjs
    // 生成 res.js
    npm run resjs
    // 在linux下用chromium浏览器测试
    // 可以修改karma.conf.js然后在其他浏览器上测试
    npm run test
