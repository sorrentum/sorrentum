"""
Import as:

import optimizer.opt_lib_tasks as ooplitas
"""

import logging
import os
from typing import Optional

from invoke import task

import helpers.hgit as hgit
import helpers.lib_tasks as hlibtask

_LOG = logging.getLogger(__name__)


_OPTIMIZER_DIR = os.path.join(hgit.get_amp_abs_path(), "optimizer")


# #############################################################################
# Docker image release.
# #############################################################################


@task
def opt_docker_build_local_image(  # type: ignore
    ctx,
    version,
    cache=True,
    base_image="",
    update_poetry=False,
):
    """
    Build a local `opt` image (i.e., a release candidate "dev" image).

    See corresponding invoke target for the main container.
    """
    hlibtask.docker_build_local_image(
        ctx,
        version,
        cache=cache,
        base_image=base_image,
        update_poetry=update_poetry,
        container_dir_name=_OPTIMIZER_DIR,
    )


@task
def opt_docker_tag_local_image_as_dev(  # type: ignore
    ctx,
    version,
    base_image="",
):
    """
    (ONLY CI/CD) Mark the `opt:local` image as `dev`.

    See corresponding invoke target for the main container.
    """
    hlibtask.docker_tag_local_image_as_dev(
        ctx,
        version,
        base_image=base_image,
        container_dir_name=_OPTIMIZER_DIR,
    )


@task
def opt_docker_push_dev_image(  # type: ignore
    ctx,
    version,
    base_image="",
):
    """
    (ONLY CI/CD) Push the `opt:dev` image to ECR.

    See corresponding invoke target for the main container.
    """
    hlibtask.docker_push_dev_image(
        ctx, version, base_image=base_image, container_dir_name=_OPTIMIZER_DIR
    )


@task
def opt_docker_release_dev_image(  # type: ignore
    ctx,
    version,
    cache=True,
    push_to_repo=True,
    update_poetry=False,
):
    """
    (ONLY CI/CD) Build, test, and release to ECR the latest `opt:dev` image.

    See corresponding invoke target for the main container.

    Phases:
    1) Build local image
    2) Mark local as dev image
    3) Push dev image to the repo
    """
    hlibtask.docker_release_dev_image(
        ctx,
        version,
        cache=cache,
        # TODO(Grisha): replace with `opt` tests.
        skip_tests=True,
        fast_tests=False,
        slow_tests=False,
        superslow_tests=False,
        # TODO(Grisha): enable `qa` tests.
        qa_tests=False,
        push_to_repo=push_to_repo,
        update_poetry=update_poetry,
        container_dir_name=_OPTIMIZER_DIR,
    )


# #############################################################################
# Docker development.
# #############################################################################


@task
def opt_docker_pull(ctx, stage="dev", version=None):  # type: ignore
    """
    Pull latest dev image corresponding to the current repo from the registry.
    """
    hlibtask._report_task()
    #
    base_image = ""
    hlibtask._docker_pull(ctx, base_image, stage, version)


@task
def opt_docker_bash(  # type: ignore
    ctx,
    base_image="",
    stage="dev",
    version="",
    entrypoint=True,
    as_user=True,
):
    """
    Start a bash shell inside the `opt` container corresponding to a stage.

    See corresponding invoke target for the main container.
    """
    hlibtask.docker_bash(
        ctx,
        base_image=base_image,
        stage=stage,
        version=version,
        entrypoint=entrypoint,
        as_user=as_user,
        container_dir_name=_OPTIMIZER_DIR,
    )


@task
def opt_docker_jupyter(  # type: ignore
    ctx,
    stage="dev",
    version="",
    base_image="",
    auto_assign_port=True,
    port=9999,
    self_test=False,
):
    """
    Run jupyter notebook server in the `opt` container.

    See corresponding invoke target for the main container.
    """
    hlibtask.docker_jupyter(
        ctx,
        stage=stage,
        version=version,
        base_image=base_image,
        auto_assign_port=auto_assign_port,
        port=port,
        self_test=self_test,
        container_dir_name=_OPTIMIZER_DIR,
    )


@task
def opt_docker_cmd(  # type: ignore
    ctx,
    base_image="",
    stage="dev",
    version="",
    cmd="",
    as_user=True,
    use_bash=False,
):
    """
    Run a command inside the `opt` container corresponding to a stage.

    See corresponding invoke target for the main container.
    """
    hlibtask.docker_cmd(
        ctx,
        base_image=base_image,
        stage=stage,
        version=version,
        cmd=cmd,
        as_user=as_user,
        use_bash=use_bash,
        container_dir_name=_OPTIMIZER_DIR,
    )


# #############################################################################
# Start/stop optimizer services.
# #############################################################################


def _get_opt_docker_up_cmd(
    detach: bool, base_image: str, stage: str, version: Optional[str]
) -> str:
    """
    Get `docker-compose up` command for the optimizer.

    E.g.,

    ```
    IMAGE=*****.dkr.ecr.us-east-1.amazonaws.com/opt:dev \
        docker-compose \
        --file devops/compose/docker-compose.yml \
        --env-file devops/env/default.env \
        up \
        -d \
        app
    ```
    :param detach: whether to run in detached mode or not
    """
    extra_env_vars = None
    extra_docker_compose_files = None
    docker_up_cmd_ = hlibtask._get_docker_base_cmd(
        base_image,
        stage,
        version,
        extra_env_vars,
        extra_docker_compose_files,
    )
    # Add up command.
    docker_up_cmd_.append(
        r"""
        up"""
    )
    if detach:
        # Run in detached mode.
        docker_up_cmd_.append(
            r"""
        -d"""
        )
    # Specify the service name.
    service = "app"
    docker_up_cmd_.append(
        rf"""
        {service}"""
    )
    #
    docker_up_cmd = hlibtask._to_multi_line_cmd(docker_up_cmd_)
    return docker_up_cmd  # type: ignore[no-any-return]


@task
def opt_docker_up(ctx, detach=True, base_image="", stage="dev", version=""):  # type: ignore
    """
    Start the optimizer as a service.
    """
    # Build `docker-compose up` cmd.
    docker_up_cmd = _get_opt_docker_up_cmd(detach, base_image, stage, version)
    # Run.
    hlibtask._run(ctx, docker_up_cmd, pty=True)


def _get_opt_docker_down_cmd(
    base_image: str, stage: str, version: Optional[str]
) -> str:
    """
    Get `docker-compose down` command for the optimizer.

    E.g.,

    ```
    IMAGE=*****.dkr.ecr.us-east-1.amazonaws.com/opt:dev \
        docker-compose \
        --file devops/compose/docker-compose.yml \
        --env-file devops/env/default.env \
        down
    ```
    """
    extra_env_vars = None
    extra_docker_compose_files = None
    docker_down_cmd_ = hlibtask._get_docker_base_cmd(
        base_image,
        stage,
        version,
        extra_env_vars,
        extra_docker_compose_files,
    )
    # Add down command.
    docker_down_cmd_.append(
        r"""
        down"""
    )
    docker_down_cmd = hlibtask._to_multi_line_cmd(docker_down_cmd_)
    return docker_down_cmd  # type: ignore[no-any-return]


@task
def opt_docker_down(ctx, base_image="", stage="dev", version=""):  # type: ignore
    """
    Bring down the optimizer service.
    """
    # Build `docker-compose down` cmd.
    docker_down_cmd = _get_opt_docker_down_cmd(base_image, stage, version)
    # Run.
    hlibtask._run(ctx, docker_down_cmd, pty=True)
