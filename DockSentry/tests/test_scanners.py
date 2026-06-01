#!/usr/bin/env python3
import pytest
import os
from docksentry.scanners.dockerfile import DockerfileScanner
from docksentry.core.engine import ContainerAuditEngine

@pytest.mark.asyncio
async def test_dockerfile_malicious_root_detection(tmp_path):
    """
    Validates that the static code analyzer surfaces a policy violation 
    when a configuration does not specify a non-root USER execution block.
    """
    d = tmp_path / "sub_folder"
    d.mkdir()
    mock_df = d / "Dockerfile"
    mock_df.write_text("FROM ubuntu:latest\nRUN apt-get update\nEXPOSE 80")

    engine = ContainerAuditEngine()
    scanner = DockerfileScanner(engine.rules)
    
    findings = await scanner.scan(str(mock_df))
    assert len(findings) > 0
    # Confirm that it caught the root or baseline dependency risk accurately
    assert any(f["id"] in ["DS-CIS-4.3", "DS-CIS-5.2"] for f in findings)