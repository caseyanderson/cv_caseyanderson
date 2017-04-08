var gulp = require('gulp');
var sass = require('gulp-sass');
var autoprefixer = require('gulp-autoprefixer');
var clean = require('gulp-clean-css');
var browserSync = require('browser-sync').create();


// store sass options
var sassOptions = {
    errLogToConsole: true,
    outputStyle: 'expanded'
};


// generic structure for files config
var config = {
    css:    'css/*.css',
    html:   'html/*.html',
    sass:   'sass/*.scss'
}


// setup browser sync, watch all css and html for changes
gulp.task( 'browser-sync', ['styles'], function() {
	browserSync.init(
        [ config.css, config.html ], {
            server: {
                baseDir: config.base
            },
        injectChanges: true
    });
});


// regenerate sass and pipe to browsersync after autoprefixer
gulp.task('styles', function() {
    return gulp.src(config.sass)
        .pipe(sass(sassOptions).on('error', sass.logError))
        .pipe(autoprefixer('last 2 versions'))
        .pipe(clean())
        .pipe(gulp.dest('css'))
        .pipe(browserSync.reload({stream: true}));
});


// watch for changes in sass and regen css if there are any
gulp.task('watch', ['browser-sync'], function () {
    gulp.watch(config.sass, ['styles']);
});

// run the tasks
gulp.task('default', ['browser-sync', 'styles', 'watch']);
