# Signing the released binary

Starting with the 0.39.0 version, the released binary for Windows is signed with a self-signed certificate linked to [Oslandia](https://oslandia.com/) (as subject).
For financial reasons it's still a self-signed certificate with:

- the Extended Key Usage (EKU) Code Signing
- a transparent and documented supply chain:
    - how the certificate has been generated (see below)
    - signing binary in [a public CI workflow](https://github.com/qgis-deployment/qgis-deployment-toolbelt-cli/actions/workflows/build_release.yml) (passwords are obvisouly securely saved in GitHub Actions secretes)
    - signed binary published as an [immutable release](https://docs.github.com/code-security/supply-chain-security/understanding-your-software-supply-chain/immutable-releases) to protect it against alterations post-release

The work has been funded by [Grenoble Alpes Métropole](https://www.grenoblealpesmetropole.fr/). This page describes what has been done to generate the certificate and consolidate knowledge about this work. If you are interested to have a signed binary with a certificate emitted by a recognized certification authority, [please reach us](../misc/funding.md).

## System requirements

- most of commands have been tested on Linux (Ubuntu 24.04):
    - openssl >= 3.0
    - optionally the [GitHub CLI](https://cli.github.com/) to set Actions secrets
- for Windows, see [this guide](../guides/howto_windows_sign_executable.md)

## Step-by-step issuance of code signing certificate

1. Generate a private key:

    ```sh
    openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:4096 -out builder/code_signing_certificate_priv.key
    ```

1. Generate a Certificate Signing Request (CSR):

    ```sh
    openssl req -new -utf8 -config builder/codesign_openssl.cnf -key builder/code_signing_certificate_priv.key -out builder/code_signing_certificate_request.csr
    ```

1. Generate the self-signed certificate (CRT) with the Code Signing EKU extension:

    ```sh
    openssl x509 -req -utf8 -days 3650 -in builder/code_signing_certificate_request.csr -signkey builder/code_signing_certificate_priv.key -extfile builder/codesign_openssl.cnf -extensions codesign_ext -out builder/code_signing_certificate.crt
    ```

1. Export the certificate and private key to a password-protected PFX file:

    ```sh
    openssl pkcs12 -export -out builder/code_signing_certificate.pfx -inkey builder/code_signing_certificate_priv.key -in builder/code_signing_certificate.crt
    ```

    You will be prompted to set a password. If you're part of Oslandia, search for `qdt_signing_pfx` in the internal passwords manager.

At this moment, 5 files have been generated (in order of appearance):

- `builder/codesign_openssl.cnf`: the config file
- `builder/code_signing_certificate_priv.key`: the private key - **THIS FILE SHOULD NEVER BE TRACKED WITH A PUBLIC GIT REPOSITORY**
- `builder/code_signing_certificate.crt`: the self-signed certificate
- `builder/code_signing_certificate_request.csr`: the certificate signing request
- `builder/code_signing_certificate.pfx`: the combined certificate and private key with password used to sign the Windows binary **THIS FILE SHOULD NEVER BE TRACKED WITH A PUBLIC GIT REPOSITORY**

## Check and inspect certificate

Get basic information:

```sh
openssl pkcs12 -info -in builder/code_signing_certificate.pfx -noout -subject
```

Get the thumbprint using:

```sh
openssl pkcs12 -in builder/code_signing_certificate.pfx -nodes | openssl x509 -noout -fingerprint -sha1
```

Export as PEM then in human readable text:

```sh
openssl pkcs12 -in builder/code_signing_certificate.pfx -nokeys -clcerts -out cert.pem
openssl x509 -in cert.pem -text -noout
# or just the subject
openssl x509 -in cert.pem -noout -subject
```

## Use the certificate in CI

:::{note}
This part is reserved to QDT maintainers.
:::

1. Upload the password used to export the PFX as Github Action secret:

    ```sh
    gh secret set WINDOWS_CERTIFICATE_PFX_PASSWORD
    ```

    Then paste the password.

1. Encode the PFX file as base64 for safe storage in environment variables:

    ```sh
    base64 -w0 builder/code_signing_certificate.pfx > builder/code_signing_certificate.pfx.b64
    ```

1. Upload it as Github Action secret:

    ```sh
    gh secret set WINDOWS_CERTIFICATE_PFX < builder/code_signing_certificate.pfx.b64
    ```

## Resources

- [Automatic Code-signing on Windows using GitHub Actions](https://federicoterzi.com/blog/automatic-codesigning-on-windows-using-github-actions/)
- [openssl official documentation](https://docs.openssl.org/3.0/)
- [How to automatically code sign the MSI with GitHub Actions](https://www.advancedinstaller.com/code-signing-with-github-actions.html)
