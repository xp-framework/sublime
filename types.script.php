<?php

use lang\ClassLoader;

function completionsIn($l, $path) {
  $namespace= $path ? $path.'.' : '';
  foreach ($l->packageContents($path) as $content) {
    $end= strlen($content) - 1;
    if ('/' === $content{$end}) {
      $package= substr($content, 0, $end);
      yield sprintf("1 %s%s\tpackage>>%s\\", $namespace, $package, strtr($package, '.', '\\'));
    } else if (strstr($content, xp::CLASS_FILE_EXT)) {
      $type= substr($content, 0, -strlen(xp::CLASS_FILE_EXT));
      yield sprintf("2 %s%s\ttype>>%s", $namespace, $type, strtr($type, '.', '\\'));
    }
  }
}

function completions($path) {
  foreach (ClassLoader::getLoaders() as $l) {
    if ($l->providesResource('autoload.php') || $l->providesResource('__xp.php')) {
      foreach (completionsIn($l, $path) as $completion) {
        yield $completion;
      }
    }
  }
}

$completions= iterator_to_array(completions($argv[1]));
sort($completions);
foreach ($completions as $completion) {
  echo substr($completion, 2), "\n";
}
