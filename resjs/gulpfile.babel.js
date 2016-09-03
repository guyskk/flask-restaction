import gulp from 'gulp'
import rename from 'gulp-rename'
import babel from 'gulp-babel'
import webpack from 'webpack-stream'

let webpackModule = {
    loaders: [{
        test: /\.js$/,
        loader: 'babel',
        exclude: /node_modules/
    }]
}

gulp.task('build:res-web', () => {
    return gulp.src('res.base.js')
        .pipe(webpack({
            entry: './res.base.js',
            output: {
                library: 'res',
                libraryTarget: 'umd',
                filename: 'res.web.js'
            },
            module: webpackModule
        }))
        .pipe(gulp.dest('./dist/'))
})

gulp.task('build:res-node', () => {
    return gulp.src('res.base.js')
        .pipe(babel())
        .pipe(rename('res.node.js'))
        .pipe(gulp.dest('./dist/'))
})

gulp.task('build:index', () => {
    return gulp.src('index.js')
        .pipe(babel())
        .pipe(gulp.dest('./dist/'))
})


gulp.task('build', ['build:res-web', 'build:res-node', 'build:index'])
gulp.task('default', ['build'])
gulp.task('watch', ['build'], () => {
    gulp.watch('*.js', ['build'])
})
