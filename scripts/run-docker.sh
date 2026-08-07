#!/usr/bin/env bash

set -Eeuo pipefail

AWS_PROFILE_NAME="${NIMBUSAUDIT_AWS_PROFILE:-nimbusaudit-readonly}"
IMAGE_NAME="${NIMBUSAUDIT_IMAGE:-nimbusaudit}"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
OUTPUT_DIR="$PROJECT_ROOT/outputs"

# Ensure required host tools are available.
if ! command -v aws >/dev/null 2>&1; then
    echo "Error: AWS CLI is not installed or not in PATH." >&2
    exit 2
fi

if ! command -v docker >/dev/null 2>&1; then
    echo "Error: Docker is not installed or not in PATH." >&2
    exit 2
fi

# Restrict permissions on anything created below this point.
umask 077

CRED_DIR="$(mktemp -d)"
CRED_FILE="$CRED_DIR/credentials"

cleanup() {
    rm -rf "$CRED_DIR"
}

trap cleanup EXIT

# Let the host AWS CLI resolve/refresh credentials and assume
# the NimbusAudit least-privilege role.
if ! EXPORTED_CREDS="$(
    aws configure export-credentials \
        --profile "$AWS_PROFILE_NAME" \
        --format env
)"; then
    echo "Error: unable to obtain AWS credentials for profile '$AWS_PROFILE_NAME'." >&2
    exit 2
fi

eval "$EXPORTED_CREDS"
unset EXPORTED_CREDS

# Ensure the credential export actually produced everything required
# for an assumed-role session.
: "${AWS_ACCESS_KEY_ID:?AWS access key was not exported}"
: "${AWS_SECRET_ACCESS_KEY:?AWS secret key was not exported}"
: "${AWS_SESSION_TOKEN:?AWS session token was not exported}"

printf '%s\n' \
    "[$AWS_PROFILE_NAME]" \
    "aws_access_key_id = $AWS_ACCESS_KEY_ID" \
    "aws_secret_access_key = $AWS_SECRET_ACCESS_KEY" \
    "aws_session_token = $AWS_SESSION_TOKEN" \
    > "$CRED_FILE"

# Secrets no longer need to remain in this shell's environment.
unset AWS_ACCESS_KEY_ID
unset AWS_SECRET_ACCESS_KEY
unset AWS_SESSION_TOKEN
unset AWS_CREDENTIAL_EXPIRATION 2>/dev/null || true

mkdir -p "$OUTPUT_DIR"

# Exit code 1 is meaningful to NimbusAudit, so capture rather than
# allowing `set -e` to terminate the wrapper immediately.
if docker run --rm \
    --mount type=bind,source="$CRED_FILE",target=/run/nimbusaudit/aws-credentials,readonly \
    --mount type=bind,source="$OUTPUT_DIR",target=/outputs \
    --env AWS_SHARED_CREDENTIALS_FILE=/run/nimbusaudit/aws-credentials \
    "$IMAGE_NAME" \
    --profile "$AWS_PROFILE_NAME" \
    "$@"
then
    EXIT_CODE=0
else
    EXIT_CODE=$?
fi

exit "$EXIT_CODE"