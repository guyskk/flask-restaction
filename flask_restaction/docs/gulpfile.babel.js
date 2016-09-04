import gulp from 'gulp'
import less from 'gulp-less'
import autoprefixer from 'gulp-autoprefixer'
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

gulp.task('build:js', () => {
    return gulp.src('docs.js')
        .pipe(webpackStream({
            entry: './docs.js',
            output: {
                filename: 'docs.js'
            },
            module: webpackModule,
            plugins: [webpackDefinePlugin]
        }))
        .pipe(gulp.dest('dist'))
})
gulp.task('build:js-min', () => {
    return gulp.src('docs.js')
        .pipe(webpackStream({
            entry: './docs.js',
            output: {
                filename: 'docs.min.js'
            },
            module: webpackModule,
            plugins: [webpackDefinePlugin, webpackUglifyJsPlugin]
        }))
        .pipe(gulp.dest('dist'))
})
gulp.task('build:css', () => {
    return gulp.src('docs.less')
        .pipe(less({
            paths: ['./']
        }))
        .pipe(autoprefixer())
        .pipe(gulp.dest('dist'))
})

gulp.task('build', ['build:js', 'build:css', 'build:js-min'])
gulp.task('default', ['build'])
gulp.task('watch', ['build'], () => {
    gulp.watch('*.*', ['build'])
})
