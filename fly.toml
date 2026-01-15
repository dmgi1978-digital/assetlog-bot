app = "assetlog-bot"
kill_signal = "SIGINT"
kill_timeout = 5
primary_region = "ams"

[build]
  builder = "paketobuildpacks/builder:base"
  buildpacks = ["gcr.io/paketo-buildpacks/python"]

[env]
  PORT = "8080"

[[services]]
  protocol = "tcp"
  internal_port = 8080
  processes = ["app"]
