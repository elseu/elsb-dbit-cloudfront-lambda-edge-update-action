import os
import boto3

cloudfront_svc = boto3.client('cloudfront')


def generate_new_distribution_config(distribution_config: dict, lambda_updated_arn: dict) -> dict:
    try:
        lambda_function_associations_list = distribution_config['DistributionConfig']['DefaultCacheBehavior']['LambdaFunctionAssociations']
        lambda_function_associations_list_updated = []
        for item in lambda_function_associations_list:
            event_type = item['EventType']
            if lambda_updated_arn[event_type] is not None:
                item['LambdaFunctionARN'] = lambda_updated_arn[event_type]
            lambda_function_associations_list_updated.append(item)
        distribution_config['DistributionConfig']['DefaultCacheBehavior']['LambdaFunctionAssociations'] = lambda_function_associations_list_updated
        return distribution_config
    except Exception as error:
        print("Error during update distribution config with new lambda ARN")
        print(error)
        exit(1)


def get_distribution_config(distribution_id: str) -> dict:
    try:
        cloudfront_svc.get_distribution_config(Id=distribution_id)
    except Exception as error:
        print("Error during get distribution config")
        print(error)
        exit(1)


def get_env_var(var_name, required):
    if var_name in os.environ:
        return os.environ[var_name]
    else:
        if required is True:
            raise RuntimeError("Required parameter " + var_name + " missing.")
        return None


# Getting the input parameters
distribution_id = get_env_var('CLOUDFRONT_ID', True)

lambdas_arn = {
    "viewer-request": get_env_var('LAMBDA_VIEWER_REQUEST_VERSION_ARN', False),
    "origin-request": get_env_var('LAMBDA_ORIGIN_REQUEST_VERSION_ARN', False),
    "origin-response": get_env_var('LAMBDA_ORIGIN_RESPONSE_VERSION_ARN', False),
    "viewer-response": get_env_var('LAMBDA_VIEWER_RESPONSE_VERSION_ARN', False)
}


distribution_config = get_distribution_config(distribution_id)
distribution_config_updated = generate_new_distribution_config(distribution_config, lambdas_arn)

cloudfront_svc.update_distribution(
    DistributionConfig=distribution_config_updated,
    Id=distribution_id,
)