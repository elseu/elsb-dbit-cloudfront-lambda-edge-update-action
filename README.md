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
           lambda_viewer_request_version_arn: <New Lambda Viewer Request version ARN>
           lambda_origin_request_version_arn: <New Lambda Origin Request version ARN>
           lambda_origin_response_version_arn: <New Lambda Origin Response version ARN>
           lambda_viewer_response_version_arn: <New Lambda Viewer Response version ARN>
```