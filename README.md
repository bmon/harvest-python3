Python 3 Harvest API Bindings
===================

A python 3 wrapper for the harvestapp API. Derived from [lionheart's python2 harvest wrapper][1]. Additional detail can be found by checking the [harvestapp api documentation][2].

Usage
-----

    import harvest
    user = harvest.Harvest('https://example.harvestapp.com', 'example@email.com', 'passw0rd')
    user.who_am_i()
    user.update_task({
        'hours': 1.8
    })
    user.get_today()

  [1]: https://github.com/lionheart/python-harvest
  [2]: https://github.com/harvesthq/api
