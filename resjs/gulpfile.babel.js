import gulp from 'gulp'
import webpack from 'webpack-stream'

let webpackModule = {
    loaders: [{
        test: /\.js$/,
        loader: 'babel',
        exclude: /node_modules/
    }]
}

gulp.task('build:res', () => {
    return gulp.src('res.base.js')
        .pipe(webpack({
            entry: './res.base.js',
            output: {
                library: 'res',
                libraryTarget: 'umd',
                filename: 'res.base.js'
            },
            module: webpackModule
        }))
        .pipe(gulp.dest('./dist/'))
})

gulp.task('build:index', () => {
    return gulp.src('index.js')
        .pipe(webpack({
            entry: './index.js',
            output: {
                library: 'resjs',
                libraryTarget: 'commonjs2',
                filename: 'index.js'
            },
            target: 'node',
            externals: ['handlebars', 'commander', 'axios'],
            node: {
                __dirname: false,
                __filename: false
            },
            module: webpackModule
        }))
        .pipe(gulp.dest('./dist/'))
})


gulp.task('build', ['build:res', 'build:index'])
gulp.task('default', ['build'])
gulp.task('watch', ['build'], () => {
    gulp.watch('*.js', ['build'])
})
