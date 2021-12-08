# Update Cloudfront distribution with new Lambda Edge version ARN

This action will:
 - get cloudfront distribution configuration
 - generate distribution configuration with new lambda version ARN
 - update the cloudfront distribution
 
 ## Usage
 
```yaml
  jobs:
    deploy:
     runs-on: ubuntu-latest
     steps:
       - uses: elseu/elsb-dbit-cloudfront-lambda-edge-update-action@v1
         with:
          
           distribution_id: <Cloudfront Distribution ID>
           path_pattern: <Cloudfront Behavior Path pattern (if DefaultCacheBehaviour, set path_pattern to 'Default')>
           lambda_association_event_type: <Lambda association Event type>
           lambda_association_version_arn: <Lambda association version ARN>
           cloudfront_invalidation_required: <Ask for Cloudfront invalidation (true/false)>
```