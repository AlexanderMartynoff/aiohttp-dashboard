let path = require('path')
let CopyWebpackPlugin = require('copy-webpack-plugin')
const VueLoaderPlugin = require('vue-loader/lib/plugin')
const autoprefixer = require('autoprefixer')


let resolve = (dir) => {
    return path.join(__dirname, dir)
}


module.exports = {
    mode: 'development',
    entry: {
        application: resolve('./application/application.js')
    },
    output: {
        path: resolve('../aiohttp_dashboard/static/bundle'),
        filename: '[name].js',
        publicPath: '/static'
    },
    resolve: {
        extensions: ['.js', '.vue'],
        alias: {
            '@': resolve('application'),
            'vue$': 'vue/dist/vue.js'
        }
    },
    module: {
        rules: [
            {
                test: /\.vue$/,
                loader: 'vue-loader'
            },
            {
                test: /\.js$/,
                exclude: /(node_modules|bower_components)/,
                use: {
                    loader: 'babel-loader',
                    options: {
                      presets: ['@babel/preset-env']
                    }
                },
            },
            {
                test: /\.s[ac]ss$/i,
                use: [
                    {
                        loader: 'style-loader'
                    },
                    {
                        loader: 'css-loader'
                    },
                    {
                        loader: 'postcss-loader',
                        options: {
                            plugins: [
                                autoprefixer({
                                    browsersist: ['ie >= 8', 'last 4 version']
                                })
                            ],
                        }
                    },
                    {
                        loader:'sass-loader'
                    }
                ],
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader']
            }
        ]
    },
    plugins: [
        new VueLoaderPlugin(),
        new CopyWebpackPlugin([
            { from: resolve('node_modules/@fortawesome/fontawesome-free/css'), to: "font-awesome/css", ignore: ["*.map"] },
            { from: resolve('node_modules/@fortawesome/fontawesome-free/webfonts'), to: "font-awesome/webfonts" },
        ])
    ]
}
