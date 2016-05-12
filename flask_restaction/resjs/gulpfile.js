var gulp = require('gulp');
var uglify = require('gulp-uglify');
var webpack = require('webpack-stream');
var rename = require("gulp-rename");

gulp.task('default', function() {
    return gulp.src('src/*.js')
        .pipe(webpack({
            entry: './src/res.js',
            output: {
                filename: 'res.js',
                library: 'res',
                libraryTarget: 'umd'
            }
        }))
        .pipe(gulp.dest('dist'))
        .pipe(uglify())
        .pipe(rename('res.min.js'))
        .pipe(gulp.dest('dist'));
});
