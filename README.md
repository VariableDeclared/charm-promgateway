# charm-promgateway

Checkout the main project at https://github.com/prometheus/pushgateway

## Description

This charm deploys pushgateway with minimum configuration.

## Usage

```
charmcraft pack

juju add-model pushgateway 
juju deploy ./pushgateway.charm
juju attach-resource pushgateway-snap=./pushgateway.snap
```


## Relations

No relations applicable.

## Contributing

Please see the [Juju SDK docs](https://juju.is/docs/sdk) for guidelines
on enhancements to this charm following best practice guidelines, and
`CONTRIBUTING.md` for developer guidance.
