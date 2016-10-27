import gulp from 'gulp'
import rename from 'gulp-rename'
import babel from 'gulp-babel'
import webpack from 'webpack'
import webpackStream from 'webpack-stream'

let webpackModule = {
    loaders: [{
        test: /\.js$/,
        loader: 'babel',
        exclude: /node_modules/
    }]
}
let webpackDefinePlugin = new webpack.DefinePlugin({
    'process.env': {
        'NODE_ENV': JSON.stringify('production')
    }
})
let webpackUglifyJsPlugin = new webpack.optimize.UglifyJsPlugin({
    compress: {
        warnings: false
    }
})

gulp.task('build:res-web', () => {
    return gulp.src('res.base.js')
        .pipe(webpackStream({
            entry: './res.base.js',
            output: {
                library: 'res',
                libraryTarget: 'umd',
                filename: 'res.web.js'
            },
            module: webpackModule,
            plugins: [webpackDefinePlugin]
        }))
        .pipe(gulp.dest('./dist/'))
})

gulp.task('build:res-web-min', () => {
    return gulp.src('res.base.js')
        .pipe(webpackStream({
            entry: './res.base.js',
            output: {
                library: 'res',
                libraryTarget: 'umd',
                filename: 'res.web.min.js'
            },
            module: webpackModule,
            plugins: [webpackDefinePlugin, webpackUglifyJsPlugin]
        }))
        .pipe(gulp.dest('./dist/'))
})

gulp.task('build:res-node', () => {
    return gulp.src('res.base.js')
        .pipe(babel())
        .pipe(rename('res.node.js'))
        .pipe(gulp.dest('./dist/'))
})

gulp.task('build:res-rn', () => {
    return gulp.src('res.rn.js')
        .pipe(rename('res.rn.js'))
        .pipe(gulp.dest('./dist/'))
})

gulp.task('build:index', () => {
    return gulp.src('index.js')
        .pipe(babel())
        .pipe(gulp.dest('./dist/'))
})


gulp.task('build', ['build:res-web', 'build:res-web-min', 'build:res-node', 'build:res-rn', 'build:index'])
gulp.task('default', ['build'])
gulp.task('watch', ['build'], () => {
    gulp.watch('*.js', ['build'])
})
