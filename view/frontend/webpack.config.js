const path = require('path');
const { CleanWebpackPlugin } = require('clean-webpack-plugin');

module.exports = {
    entry: {
        dev: './src/index.js'
    },
    plugins: [
        new CleanWebpackPlugin(),
    ],
    output: {
      filename: 'main.js',
        path: path.resolve(__dirname, 'static/js')
    },
    module: {
        rules: [
            {
                test: /\.(js|mjs|jsx|ts|tsx)$/,
                exclude: /node_modules/,
                use: {
                  loader: "babel-loader"
                }
            },
            {
                test: /\.scss$/,
                include: /src/,
                use: [
                    'style-loader',
                    'css-loader',
                    'sass-loader'
                ]
            },
            {
                test: /\.css$/,
                include: /src/,
                use: [
                    'style-loader',
                    'css-loader'
                ]
            }
        ]
    },
    devServer: {
        writeToDisk: true,
        stats: 'errors-only'
    }
}