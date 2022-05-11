module.exports = {
    mode: "development",
    devtool: "source-map",
    entry: {
        app: ["./src/index.tsx"]
    },
    output: {
        path: path.resolve(__dirname, "build")
        publicPath: "/assets/",
        filename: "bundle.js"
    }

    resolve: {
        extensions: [".js", ".ts", ".tsx"]
    },

    module: {
        rules: [
            {
                test: /\.ts(x?)$/,
                exclude: /node_modules/,
                use: [
                    {
                        loader: "ts-loader"
                    }
                ]
            },
            {
                enforce: "pre",
                test: /\.js$/,
                exclude: /node_modules/,
                loader: "source-map-loader"
            }
        ],
    },

    devServer: {
        overlay: true,
        host: '0.0.0.0',
        sockPort: 443,
        allowedHosts: ['localhost', '.gitpod.io'],
    },

    externals: {
        "react": "React",
        "react-dom": "ReactDOM"
    }
};
