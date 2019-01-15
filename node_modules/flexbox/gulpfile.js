var gulp    = require('gulp'),
    sass    = require('gulp-sass'),
    rename  = require('gulp-rename'),
    cssmin  = require('gulp-minify-css');

gulp.task('scss', function() {
  return gulp.src('scss/*.scss')
    .pipe(sass())
    .pipe(gulp.dest('css'))
    .pipe(cssmin())
    .pipe(rename({ suffix: '.min' }))
    .pipe(gulp.dest('css'));
});

gulp.task('watch', function() {
  gulp.watch('scss/*.scss', ['scss']);
});

gulp.task('default', ['scss', 'watch']);
