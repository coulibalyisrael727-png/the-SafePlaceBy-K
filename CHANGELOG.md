# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-05-13
### Added
- Initial release of The SafePlace by K
- Django main application with podcast, video, and live streaming capabilities
- REST API using Django REST Framework for dashboard integration
- Custom Dashboard microservice with Tailwind CSS
- Secure API Key authentication between services
- Stripe and PayPal donation integrations
- Newsletter and notification subscription system

### Changed
- Refactored legacy UI to use a 3D-immersive design for the homepage and live streams
- Replaced basic authentication with API Key authentication for the dashboard

### Fixed
- Fixed API routes for episode publishing from the dashboard
- Fixed cross-service communication using correct API URLs
